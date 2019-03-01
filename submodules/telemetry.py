# TODO: Uses placeholder variables in other files, so make it use actual values
# TODO: what if radio turned off during a burst?
import base64
import collections
import logging
import struct
import time
from functools import partial
from threading import Lock

from core import config
from helpers.threadhandler import ThreadHandler
from . import adcs
from . import radio_output
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
    :param event: message to enqueue, **MUST BE EXACTLY** 16 bytes
    """

    if len(event.encode('utf-8')) != 16:
        logger.error("Event message must be exactly 16 bytes, message is " +
                     str(len(event.encode('utf-8'))) + " bytes long")
        return

    global event_packet_buffer
    packet = "Z"
    packet += str(base64.b64encode(struct.pack('d', time.time())))
    packet += event
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


def send(ignoreADCS=False, radio="aprs"):
    """
    Concatenates packets to fit in max_packet_size (defined in config) and send through the APRS, dequing the packets in the process
    :param ignoreADCS: If true, ignores ADCS canTJBeSeen.
    :param radio: Radio to send telemetry over, either "aprs" or "iridium"
    """
    global packetBuffers, event_packet_buffer, telem_packet_buffer, packet_lock
    squishedPackets = ""

    with packet_lock:
        # packet_lock.acquire()
        while len(event_packet_buffer) + len(telem_packet_buffer) > 0 and (adcs.can_TJ_be_seen() or ignoreADCS):
            for buffer in packetBuffers:
                while len(buffer) > 0 and len(squishedPackets) < config['telemetry']['max_packet_size'] and (
                        adcs.can_TJ_be_seen() or ignoreADCS):
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


def start():
    """
    Starts the telemetry send thread
    """

    t2 = ThreadHandler(target=partial(telemetry_send),
                       name="telemetry-telemetry_send")
    t2.start()


# TODO: Need to know what needs to be done in low power and emergency modes.
def enter_emergency_mode():
    pass  # TODO: change config


def enter_low_power_mode():
    pass
