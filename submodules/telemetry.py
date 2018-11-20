# uses placeholder variables in other files. TODO: make it use actual values
import base64
import logging
import struct
import time
from functools import partial
from threading import Lock

from core import config
from submodules.threadhandler import ThreadHandler
from . import adcs
from . import aprs
from . import gps
from . import iridium
from . import radio_output

packet_buffer = []  # telem packet list TODO: much better handling of telemetry packets
packet_lock = Lock()  # TODO: Use an indexed system so that we have persistent log storage and querying
logger = logging.getLogger("Telemetry")


def telemetry_collection():
    global packet_buffer
    while True:
        # TODO: aggregate and prioritize
        # Collect subpackets, aggregate, and prioritize
        # Aquire the send lock so that we don't add packets while bursting
        packet_lock.acquire()
        # GPS
        if time.time() % config['telemetry']['subpackets']['gps']['interval'] < 1:
            packet_buffer.append(gps_subpacket())
        # Comms
        if time.time() % config['telemetry']['subpackets']['comms']['interval'] < 1:
            packet_buffer.append(comms_subpacket())
        # ADCS
        if time.time() % config['telemetry']['subpackets']['adcs']['interval'] < 1:
            packet_buffer.append(adcs_subpacket())
        # logger.debug("Packet Buffer is %d long" % len(packet_buffer))
        packet_lock.release()
        time.sleep(1)


def telemetry_send():
    while True:
        if time.time() % config['telemetry']['send_interval'] < 1 and adcs.can_TJ_be_seen():
            logger.debug("---------------------------------hi")
            send()
            logger.debug(len(packet_buffer))
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
    global packet_buffer
    packet_lock.acquire()
    for packet in packet_buffer:
        radio_output.send(packet, None)  # radio is set to default; change if necessary
        packet_buffer.remove(packet)
        logger.debug(len(packet_buffer))
    logger.debug("Done dumping packets")
    packet_lock.release()


def on_startup():
    t1 = ThreadHandler(target=partial(telemetry_collection), name="telemetry-telemetry_collection")
    t1.start()

    t2 = ThreadHandler(target=partial(telemetry_send), name="telemetry-telemetry_send")
    t2.start()


def enter_emergency_mode():
    pass  # TODO: change config


def enter_low_power_mode():
    pass
