#pushed 10/10/18 by Patrick Zhang, uses placeholder variables in other files

import base64
import struct
import threading
import time

import core, sys
from core import config
from . import command_ingest
from . import eps
from . import gps
from . import radio_output
from . import aprs
from . import adcs
from . import iridium

import time
import logging

listTelemPackets = []   # telem packet list
sendingPackets = False  # don't add packets while sending them
logger = logging.getLogger("TELEM")

def telemetry_collection():
    global listTelemPackets, lastGPSsubpacket, lastCommssubpacket, lastADCSsubpacket
    while True:
        # Collect subpackets, aggregate, and prioritize
	    #GPS
        if(time.time()%config['telemetry']['subpackets']['gps']['interval'] < 1 and sendingPackets == False and time.time() % config['telemetry']['send_interval'] > 5):
            lastGPSsubpacket = gps_subpacket()
            listTelemPackets.append(gps_subpacket())
        # Comms
        if(time.time()%config['telemetry']['subpackets']['comms']['interval'] < 1 and sendingPackets == False and time.time() % config['telemetry']['send_interval'] > 5):
            lastCommssubpacket = comms_subpacket()
            listTelemPackets.append(lastCommssubpacket)
        # ADCS
        if(time.time()%config['telemetry']['subpackets']['adcs']['interval'] < 1 and sendingPackets == False and time.time() % config['telemetry']['send_interval'] > 5):
            lastADCSsubpacket = adcs_subpacket()
            listTelemPackets.append(lastADCSsubpacket)
        time.sleep(1)

def telemetry_send():
    while True:
        if (time.time() % config['telemetry']['send_interval'] < 1 and adcs.can_TJ_be_seen() == True):
            beg_count = len(listTelemPackets)
            send()
            logger.debug("Sent " + str(beg_count - len(listTelemPackets)) + " telemetry packets")
        time.sleep(1)

def gps_subpacket():
    #packet header
	packet = "G"
	#Time
	packet+=str(base64.b64encode(struct.pack('f',time.time())))
	#GPS coords
	packet+=str(base64.b64encode(struct.pack('fff',gps.lat,gps.lon,gps.alt)))
	#radio_output.send_immediate_raw(packet)
	return packet


def adcs_subpacket():
	#packet header
	packet = "A"
	#time
	packet+=str(base64.b64encode(struct.pack('f',time.time())))
	#pitch,roll,yaw
	pitch,roll,yaw = adcs.get_pry()
	packet+=str(base64.b64encode(struct.pack("ddd",pitch,roll,yaw)))
	#absolute x,y,z
	absx,absy,absz = adcs.get_abs()
	packet+=str(base64.b64encode(struct.pack("fff",absx,absy,absz)))
	#mag x,y,z
	magx,magy,magz = adcs.get_mag()
	packet+=str(base64.b64encode(struct.pack("ddd",magx,magy,magz)))
	#radio_output.send_immediate_raw(packet)
	return packet

def comms_subpacket():
	#packet header
	packet = "C"
	#Time
	packet+=str(base64.b64encode(struct.pack('f',time.time())))
	#APRS info
	packet+=str(base64.b64encode(struct.pack('d',aprs.total_received_ph)))
	packet+=str(base64.b64encode(struct.pack('d',aprs.success_checksum_ph)))
	packet+=str(base64.b64encode(struct.pack('d',aprs.fail_checksum_ph)))
	packet+=str(base64.b64encode(struct.pack('d',aprs.sent_messages_ph)))
	#IRIDIUM info
	packet+=str(base64.b64encode(struct.pack('d',iridium.total_received_ph)))
	packet+=str(base64.b64encode(struct.pack('d',iridium.success_checksum_ph)))
	packet+=str(base64.b64encode(struct.pack('d',iridium.fail_checksum_ph)))
	packet+=str(base64.b64encode(struct.pack('d',iridium.sent_messages_ph)))
	#radio_output.send_immediate_raw(packet)
	return packet

def system_subpacket():
    pass

def last_gps_subpacket():
    global lastGPSsubpacket
    return lastGPSsubpacket

def last_comms_subpacket():
    global lastCommssubpacket
    return lastCommssubpacket

def last_adcs_subpacket():
    global lastADCSsubpacket
    return lastADCSsubpacket

# Sends the queued packets through radio_output
def send():
    global listTelemPackets, sendingPackets
    sendingPackets = True
    for packet in listTelemPackets:
        radio_output.send(packet, None) # radio is set to default; change if necessary
        time.sleep(1)
        listTelemPackets.remove(packet)
    sendingPackets = False


def on_startup():
    t = threading.Thread(target=telemetry_collection, daemon=True)
    t.start()

    t2 = threading.Thread(target=telemetry_send, daemon=True)
    t2.start()


def enter_emergency_mode():
    pass


def enter_low_power_mode():
    pass
