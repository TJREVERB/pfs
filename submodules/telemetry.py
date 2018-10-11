#pushed 10/10/18 by Patrick Zhang, uses placeholder variables in other files

import base64
import struct
import threading
import time

import core
from core import config
from . import command_ingest
from . import eps
from . import gps
from . import radio_output
from . import aprs
from . import adcs
from . import iridium


def telemetry_collection():
    while True:
        # Collect subpackets, aggregate, and prioritize
        pass


def gps_subpacket():
    #packet header
	packet = "G"
	#Time
	packet+=base64.b64encode(struct.pack('f',time.time()))
	#GPS coords
	packet+=base64.b64encode(struct.pack('fff',gps.lat,gps.lon,gps.alt))
	radio_output.send_immediate_raw(packet)


def adcs_subpacket():
	#packet header
	packet = "A"
	#time
	packet+=base64.b64encode(struct.pack('f',time.time()))
	#pitch,roll,yaw
	pitch,roll,yaw = adcs.get_pry()
	packet+=base64.b64encode(struct.pack("ddd",pitch,roll,yaw))
	#absolute x,y,z
	absx,absy,absz = adcs.get_abs()
	packet+=base64.b64encode(struct.pack("fff",absx,absy,absz))
	#mag x,y,z
	magx,magy,magz = adcs.get_mag()
	packet+=base64.b64encode(struct.pack("ddd",magx,magy,magz))
	radio_output.send_immediate_raw(packet)


def comms_subpacket():
	#packet header
	packet = "C"
	#Time
	packet+=base64.b64encode(struct.pack('f',time.time()))
	#APRS info
	packet+=base64.b64encode(struct.pack('d',aprs.total_received_ph))
	packet+=base64.b64encode(struct.pack('d',aprs.success_checksum_ph))
	packet+=base64.b64encode(struct.pack('d',aprs.fail_checksum_ph))
	packet+=base64.b64encode(struct.pack('d',aprs.sent_messages_ph))
	#IRIDIUM info
	packet+=base64.b64encode(struct.pack('d',iridium.total_received_ph))
	packet+=base64.b64encode(struct.pack('d',iridium.success_checksum_ph))
	packet+=base64.b64encode(struct.pack('d',iridium.fail_checksum_ph))
	packet+=base64.b64encode(struct.pack('d',iridium.sent_messages_ph))
	radio_output.send_immediate_raw(packet)


def system_subpacket():
    pass


def on_startup():
    t = threading.Thread(target=telemetry_collection, daemon=True)
    t.start()


def enter_emergency_mode():
    pass


def enter_low_power_mode():
    pass
