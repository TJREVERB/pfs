# TODO: Uses placeholder variables in other files, so make it use actual values
# TODO: what if radio turned off during a burst?
import base64
import logging
import struct
import time
import collections
from functools import partial
from threading import Lock

import core, sys
from core import config
from helpers.threadhandler import ThreadHandler
from . import gps
from . import iridium
from . import radio_output
from . import aprs
from . import adcs
from . import iridium
from . import command_ingest
from .command_ingest import command

telem_packet_buffer = collections.deque(maxlen=config['telemetry']['buffer_size'])
event_packet_buffer = collections.deque(maxlen=config['telemetry']['buffer_size'])
packetBuffers = [event_packet_buffer, telem_packet_buffer]
packet_lock = Lock()  # TODO: Use an indexed system so that we have persistent log storage and querying
logger = logging.getLogger("Telemetry")


def telemetry_collection():
    global telem_packet_buffer
    while True:
        with packet_lock:
            # TODO: aggregate and prioritize
            # Collect subpackets, aggregate, and prioritize
            # Aquire the send lock so that we don't add packets while bursting
            #packet_lock.acquire()
            # GPS
            #if time.time() % config['telemetry']['subpackets']['gps']['interval'] < 1:
            try:
                telem_packet_buffer.append(gps_subpacket())
            except Exception as err:
                logger.error("Exception: " + str(err)) #TODO: handle exceptions better
            # Comms
            #if time.time() % config['telemetry']['subpackets']['comms']['interval'] < 1:
            try:
                telem_packet_buffer.append(comms_subpacket())
            except Exception as err:
                logger.error("Exception: " + str(err))
            # ADCS
            #if time.time() % config['telemetry']['subpackets']['adcs']['interval'] < 1:
            try:
                telem_packet_buffer.append(adcs_subpacket())
            except Exception as err:
                logger.error("Exception: " + str(err))
            # logger.debug("Packet Buffer is %d long" % len(packet_buffer))
            #packet_lock.release()
        time.sleep(config['telemetry']['subpackets'])
        #print(telem_packet_buffer)


def telemetry_send():
    """
    Thread method to burst the telemetry every so often
    """
    # TODO: check battery levels
    global telem_packet_buffer, event_packet_buffer
    time.sleep(60)

    while True:
        if (adcs.can_TJ_be_seen() == True and len(telem_packet_buffer) + len(event_packet_buffer) > 0):
            telemetry_send_once()
        time.sleep(config['telemetry']['send_interval'])

def telemetry_send_once():
    """
    Immediately send telemetry packets in both telemetry and event packet queues
    """
    global telem_packet_buffer, event_packet_buffer
    beg_count = len(telem_packet_buffer) + len(event_packet_buffer)
    send()
    logger.debug("Sent " + str(beg_count - len(telem_packet_buffer) - len(event_packet_buffer)) + " telemetry packets")

@command("burst")
def telemetry_burst_command():
    """
    Burst command; ignores isTJseen and other checks
    """
    send(ignoreAPRS=True)

def gps_subpacket():
    """
    Return a GPS subpacket
    """
    # packet header
    packet = "G"
    # Time
    packet += base64.b64encode(struct.pack('d', time.time())).decode('UTF-8')
    # GPS coords
    # TODO fix this packet += base64.b64encode(struct.pack('fff', gps.lat, gps.lon, gps.alt)).decode('UTF-8')
    packet += base64.b64encode(struct.pack('fff', -1, -1, -1)).decode('UTF-8')
    # radio_output.send_immediate_raw(packet)

    return packet


def adcs_subpacket():
    """
    Return an ADCS subpacket
    """
    # packet header
    packet = "A"
    # time
    packet += base64.b64encode(struct.pack('d', time.time())).decode('UTF-8')
    # pitch,roll,yaw
    pitch, roll, yaw = adcs.get_pry()
    packet += base64.b64encode(struct.pack("ddd", pitch, roll, yaw)).decode('UTF-8')
    # absolute x,y,z
    absx, absy, absz = adcs.get_abs()
    packet += base64.b64encode(struct.pack("fff", absx, absy, absz)).decode('UTF-8')
    # mag x,y,z
    magx, magy, magz = adcs.get_mag()
    packet += base64.b64encode(struct.pack("ddd", magx, magy, magz)).decode('UTF-8')
    # radio_output.send_immediate_raw(packet)

    return packet


def comms_subpacket():
    """
    Return a comms subpacket
    """
    # packet header
    packet = "C"
    # Time
    packet += base64.b64encode(struct.pack('d', time.time())).decode('UTF-8')
    # Sequence number
    #packet += base64.b64encode(struct.pack('i', comms_sequence_number)).decode('UTF-8')
    # APRS info
    packet += base64.b64encode(struct.pack('d', aprs.total_received_ph)).decode('UTF-8')
    packet += base64.b64encode(struct.pack('d', aprs.success_checksum_ph)).decode('UTF-8')
    packet += base64.b64encode(struct.pack('d', aprs.fail_checksum_ph)).decode('UTF-8')
    packet += base64.b64encode(struct.pack('d', aprs.sent_messages_ph)).decode('UTF-8')
    # IRIDIUM info
    packet += base64.b64encode(struct.pack('d', iridium.total_received_ph)).decode('UTF-8')
    packet += base64.b64encode(struct.pack('d', iridium.success_checksum_ph)).decode('UTF-8')
    packet += base64.b64encode(struct.pack('d', iridium.fail_checksum_ph)).decode('UTF-8')
    packet += base64.b64encode(struct.pack('d', iridium.sent_messages_ph)).decode('UTF-8')
    # radio_output.send_immediate_raw(packet)
    return packet

#TODO: add in system subpackets
def system_subpacket():
    pass

#TODO: EPS subpacket

def enqueue_event_message(event):
    """
    Enqueue an event message.
    event - message to enqueue, **MUST BE EXACTLY** 16 bytes
    """

    if len(event.encode('utf-8')) != 16:
        logger.error("Event message must be exactly 16 bytes, message is " + str(len(event.encode('utf-8'))) + " bytes")
        return

    global event_packet_buffer
    packet = "Z"
    packet += str(base64.b64encode(struct.pack('d', time.time())))
    packet += event
    event_packet_buffer.append(packet)

def send(ignoreADCS=False):
    """
    Concatenates packets to fit in max_packet_size (defined in config) and send through the APRS, dequing the packets in the process
    """
    global packetBuffers, event_packet_buffer, telem_packet_buffer
    squishedPackets = ""

    with packet_lock:
        #packet_lock.acquire()
        while len(event_packet_buffer)+len(telem_packet_buffer) > 0 and (adcs.can_TJ_be_seen() or ignoreADCS):
            for buffer in packetBuffers:
                while len(buffer) > 0 and len(squishedPackets) < config['telemetry']['max_packet_size'] and (adcs.can_TJ_be_seen() or ignoreADCS):
                    #test = buffer.pop()
                    #print(test)
                    #squishedPackets += test
                    squishedPackets += buffer.pop()

            #TODO: alternate between radios
            logger.debug(squishedPackets)
            radio_output.send(squishedPackets)
            squishedPackets = ""
            time.sleep(6)

    #packet_lock.release()

def start():
    """
    Starts the telemetry collection and telemetry send threads
    """
    t1 = ThreadHandler(target=partial(telemetry_collection), name="telemetry-telemetry_collection")
    t1.start()

    t2 = ThreadHandler(target=partial(telemetry_send), name="telemetry-telemetry_send")
    t2.start()


    print(gps.get_position_packet())

# TODO: Need to know what needs to be done in low power and emergency modes.
def enter_emergency_mode():
    pass  # TODO: change config


def enter_low_power_mode():
    pass

