# pushed 10/10/18 by Patrick Zhang, uses placeholder variables in other files

import base64
import struct
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

from submodules.threadhandler import ThreadHandler
from functools import partial

listTelemPackets = []  # telem packet list
sendingPackets = False  # don't add packets while sending them


def telemetry_collection():
    global listTelemPackets
    while True:
        # Collect subpackets, aggregate, and prioritize
        # GPS
        if (time.time() % config['telemetry']['subpackets']['gps']['interval'] < 1 and sendingPackets == False):
            listTelemPackets.append(gps_subpacket())
        # Comms
        if (time.time() % config['telemetry']['subpackets']['comms']['interval'] < 1 and sendingPackets == False):
            listTelemPackets.append(comms_subpacket())
        # ADCS
        if (time.time() % config['telemetry']['subpackets']['adcs']['interval'] < 1 and sendingPackets == False):
            listTelemPackets.append(adcs_subpacket())

        print(len(listTelemPackets))
        time.sleep(1)


def telemetry_send():
    while True:
        if (time.time() % config['telemetry']['send_interval'] < 1 and adcs.can_TJ_be_seen() == True):
            print("---------------------------------hi")
            send()
            print(len(listTelemPackets))
        time.sleep(1)


def gps_subpacket():
    # packet header
    packet = "G"
    # Time
    packet += str(base64.b64encode(struct.pack('f', time.time())))
    # GPS coords
    packet += str(base64.b64encode(struct.pack('fff', gps.lat, gps.lon, gps.alt)))
    # radio_output.send_immediate_raw(packet)
    return packet


def adcs_subpacket():
    # packet header
    packet = "A"
    # time
    packet += str(base64.b64encode(struct.pack('f', time.time())))
    # pitch,roll,yaw
    pitch, roll, yaw = adcs.get_pry()
    packet += str(base64.b64encode(struct.pack("ddd", pitch, roll, yaw)))
    # absolute x,y,z
    absx, absy, absz = adcs.get_abs()
    packet += str(base64.b64encode(struct.pack("fff", absx, absy, absz)))
    # mag x,y,z
    magx, magy, magz = adcs.get_mag()
    packet += str(base64.b64encode(struct.pack("ddd", magx, magy, magz)))
    # radio_output.send_immediate_raw(packet)
    return packet


def comms_subpacket():
    # packet header
    packet = "C"
    # Time
    packet += str(base64.b64encode(struct.pack('f', time.time())))
    # APRS info
    packet += str(base64.b64encode(struct.pack('d', aprs.total_received_ph)))
    packet += str(base64.b64encode(struct.pack('d', aprs.success_checksum_ph)))
    packet += str(base64.b64encode(struct.pack('d', aprs.fail_checksum_ph)))
    packet += str(base64.b64encode(struct.pack('d', aprs.sent_messages_ph)))
    # IRIDIUM info
    packet += str(base64.b64encode(struct.pack('d', iridium.total_received_ph)))
    packet += str(base64.b64encode(struct.pack('d', iridium.success_checksum_ph)))
    packet += str(base64.b64encode(struct.pack('d', iridium.fail_checksum_ph)))
    packet += str(base64.b64encode(struct.pack('d', iridium.sent_messages_ph)))
    # radio_output.send_immediate_raw(packet)
    return packet


def system_subpacket():
    pass


# Sends the queued packets through radio_output
def send():
    global listTelemPackets, sendingPackets
    sendingPackets = True
    for packet in listTelemPackets:
        radio_output.send(packet, None)  # radio is set to default; change if necessary
        listTelemPackets.remove(packet)
        print(len(listTelemPackets))
    print("done")
    sendingPackets = False


def on_startup():
    t1 = ThreadHandler(target=partial(telemetry_collection), name="telemetry-telemetry_collection")
    t1.start()

    t2 = ThreadHandler(target=partial(telemetry_send), name="telemetry-telemetry_send")
    t2.start()


def enter_emergency_mode():
    pass


def enter_low_power_mode():
    pass
