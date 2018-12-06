# uses placeholder variables in other files. TODO: make it use actual values
import base64
import logging
import struct
import time
import collections
from functools import partial
from threading import Lock

import core, sys
from core import config
from core.threadhandler import ThreadHandler
from . import adcs
from . import aprs
from . import gps
from . import iridium
from . import radio_output
from . import aprs
from . import adcs
from . import iridium

telem_packet_buffer = collections.deque(maxlen=config['telemetry']['buffer_size'])
event_packet_buffer = collections.deque(maxlen=config['telemetry']['buffer_size'])
packetBuffers = [event_packet_buffer, telem_packet_buffer]
packet_lock = Lock()  # TODO: Use an indexed system so that we have persistent log storage and querying
logger = logging.getLogger("Telemetry")

def telemetry_collection():
    global telem_packet_buffer
    while True:
        # TODO: aggregate and prioritize
        # Collect subpackets, aggregate, and prioritize
        # Aquire the send lock so that we don't add packets while bursting
        packet_lock.acquire()
        # GPS
        if time.time() % config['telemetry']['subpackets']['gps']['interval'] < 1:
            try:
                telem_packet_buffer.append(gps_subpacket())
            except e:
                logger.debug("exception" + str(e))
        # Comms
        if time.time() % config['telemetry']['subpackets']['comms']['interval'] < 1:
            try:
                telem_packet_buffer.append(comms_subpacket())
            except e:
                logger.debug("exception" + str(e))
        # ADCS
        if time.time() % config['telemetry']['subpackets']['adcs']['interval'] < 1:
            try:
                telem_packet_buffer.append(adcs_subpacket())
            except e:
                logger.debug("exception" + str(e))
        # logger.debug("Packet Buffer is %d long" % len(packet_buffer))
        packet_lock.release()
        time.sleep(1)


def telemetry_send():
    global telem_packet_buffer, event_packet_buffer
    while True:
        if (time.time() % config['telemetry']['send_interval'] < 1 and adcs.can_TJ_be_seen() == True and len(telem_packet_buffer) + len(event_packet_buffer) > 0):
            beg_count = len(telem_packet_buffer) + len(event_packet_buffer)
            send()
            logger.debug("Sent " + str(beg_count - len(telem_packet_buffer) - len(event_packet_buffer)) + " telemetry packets")
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

#TODO: add in system subpackets
def system_subpacket():
    pass

#TODO: EPS subpacket

def last_telem_subpacket():
    global telem_packet_buffer
    return telem_packet_buffer[-1]

def last_event_subpacket():
    global event_packet_buffer
    return event_packet_buffer[-1]

def event_message(event):
    global event_packet_buffer
    packet = "Z"
    packet += str(base64.b64encode(struct.pack('f', time.time())))
    packet += event
    event_packet_buffer.append(packet)

def send():
    global packetBuffers, event_packet_buffer, telem_packet_buffer
    squishedPackets = ""

    while len(event_packet_buffer)+len(telem_packet_buffer) > 0 and adcs.can_TJ_be_seen():
        for buffer in packetBuffers:
            while len(buffer) > 0 and len(squishedPackets) < config['telemetry']['max_packet_size'] and adcs.can_TJ_be_seen():
                squishedPackets += buffer.pop()

        #TODO: alternate between radios
        radio_output.send(squishedPackets)
        squishedPackets = ""




    """while len(event_packet_buffer) + len(telem_packet_buffer) > 0:
    while len(squishedPackets) < config['telemetry']['max_packet_size']:
        for buffer in packetBuffers:
            while len(buffer) > 0 and len(squishedPackets) < config['telemetry']['max_packet_size']:
                squishedPackets += buffer.pop()
            if len(squishedPackets) > config['telemetry']['max_packet_size']:
                break"""

def on_startup():
    t1 = ThreadHandler(target=partial(telemetry_collection), name="telemetry-telemetry_collection")
    t1.start()

    t2 = ThreadHandler(target=partial(telemetry_send), name="telemetry-telemetry_send")
    t2.start()


def enter_emergency_mode():
    pass  # TODO: change config


def enter_low_power_mode():
    pass
