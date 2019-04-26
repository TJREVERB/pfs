# TODO: Uses placeholder variables in other files, so make it use actual values
# TODO: what if radio turned off during a burst?
import base64
import collections
import logging
import struct
import time
from functools import partial
from threading import Lock

from core.mode import Mode

from core import config
from core.threadhandler import ThreadHandler
#from submodules import adcs
from submodules import radio_output
from .command_ingest import command

logger = logging.getLogger("TELEMETRY")

telem_packet_buffer = collections.deque(
    maxlen=config['telemetry']['buffer_size'])
event_packet_buffer = collections.deque(
    maxlen=config['telemetry']['buffer_size'])
packetBuffers = [event_packet_buffer, telem_packet_buffer]
# TODO: Use an indexed system so that we have persistent log storage and querying
packet_lock = Lock()


def telemetry_send():
    """
    Thread method to burst the telemetry every so often
    """
    # TODO: check battery levels before sending
    global telem_packet_buffer, event_packet_buffer
    time.sleep(60)  # Don't send packets straight away

    while True:
        while state == Mode.NORMAL:
            # TODO if (adcs.can_TJ_be_seen() == True and len(telem_packet_buffer) + len(event_packet_buffer) > 0):
            if (len(telem_packet_buffer) + len(event_packet_buffer) > 0):
                telemetry_send_once()
            time.sleep(config['telemetry']['send_interval'])
        time.sleep(1)


def telemetry_send_once():
    """
    Immediately send telemetry packets in both telemetry and event packet queues
    """
    global telem_packet_buffer, event_packet_buffer
    beg_count = len(telem_packet_buffer) + len(event_packet_buffer)
    send()
    logger.debug("Sent " + str(beg_count - len(telem_packet_buffer) -
                               len(event_packet_buffer)) + " telemetry packets")


@command("burst")
def telemetry_burst_command():
    """
    Burst command; ignores isTJseen and other checks.
    """
    send(ignoreADCS=True)


def enqueue_event_message(event):
    """
    Enqueue an event message.
    Event messages are a code representing the error, for instance "I01" for IMU error #1 which is to be looked up in a table upon receipt.
    :param event: message to enqueue following code above. There is a table of codes in Google Sheets. Maximum three bytes.
    """

    if len(event.encode('utf-8')) != 3:
        logger.error("Event message larger than 3 bytes, message is " +
                     str(len(event.encode('utf-8'))) + " bytes long")
        return

    global event_packet_buffer, packet_lock
    with packet_lock:
        packet = "Z"
        packet += str(base64.b64encode(struct.pack('d', time.time())))
        packet += str(base64.b64encode(event))
        event_packet_buffer.append(packet)


def enqueue_submodule_packet(packet):
    """
    Accepts a single raw string packet and enqueues them into the telemetry packet buffer.
    :param packet: A correctly formatted string subpacket to enqueue.
    """
    global telem_packet_buffer, packet_lock
    with packet_lock:
        telem_packet_buffer.append(packet)


def enqueue_submodule_packets(packets):
    """
    Accepts raw string packets and enqueues them into the telemetry packet buffer.
    :param packets: A list of string subpackets to enqueue. These packets must be formatted correctly
    """
    global telem_packet_buffer, packet_lock
    with packet_lock:
        for packet in packets:
            telem_packet_buffer.append(packet)


def send(ignoreADCS=False, radio='aprs'):
    """
    Concatenates packets to fit in max_packet_size (defined in config) and send through the APRS, dequing the packets in the process
    :param ignoreADCS: If true, ignores ADCS canTJBeSeen.
    :param radio: Radio to send telemetry over, either "aprs" or "iridium"
    """
    global packetBuffers, event_packet_buffer, telem_packet_buffer, packet_lock
    squishedPackets = ""

    with packet_lock:
        # packet_lock.acquire()
        # TODO while len(event_packet_buffer) + len(telem_packet_buffer) > 0 and (adcs.can_TJ_be_seen() or ignoreADCS):
        while len(event_packet_buffer) + len(telem_packet_buffer) > 0:
            for buffer in packetBuffers:
                # TODO while len(buffer) > 0 and len(squishedPackets) < config['telemetry']['max_packet_size'] and (adcs.can_TJ_be_seen() or ignoreADCS):
                while len(buffer) > 0 and len(squishedPackets) < config['telemetry']['max_packet_size']:
                    # test = buffer.pop()
                    # print(test)
                    # squishedPackets += test
                    squishedPackets += buffer.pop()

            # TODO: alternate between radios
            logger.debug(squishedPackets)
            radio_output.send(squishedPackets, radio)
            squishedPackets = ""
            time.sleep(6)

    # packet_lock.release()


@command("clear")
def clear_buffers():
    global packet_lock, event_packet_buffer, telem_packet_buffer
    with packet_lock:
        event_packet_buffer.clear()
        telem_packet_buffer.clear()


def start():
    """
    Starts the telemetry send thread
    """
    global state
    state = None

    t2 = ThreadHandler(target=partial(telemetry_send), name="telemetry-telemetry_send")
    t2.start()


def enter_normal_mode():
    global state
    state = Mode.NORMAL


def enter_low_power_mode():
    global state
    state = Mode.LOW_POWER


def enter_emergency_mode():
    global state
    state = Mode.EMERGENCY
