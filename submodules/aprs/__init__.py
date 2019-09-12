import logging
import pty
import time
from functools import partial

import serial

from core import config
from core.mode import Mode
from core.helpers import is_simulate
from core.threadhandler import ThreadHandler
from submodules import command_ingest
from submodules import eps


# Placeholder values for `telemetry.py`
total_received_ph = 100
success_checksum_ph = 60
fail_checksum_ph = 40
sent_messages_ph = 50

# Initialize global variables
logger = logging.getLogger("APRS")
last_telem_time = time.time()
last_message_time = time.time()

bperiod = 60
ser = None  # Initialize serial

ser_master, ser_slave = pty.openpty()  # Serial ports for when in simulate mode


@command_ingest.command("aprs_echo", str)
def send(ser, msg: str) -> None:
    """
    Put a packet in the APRS queue.  The APRS queue exists
    only to make sure that we don't send and receive at the
    same time.
    :param msg: Message to send into the APRS queue.
    """
    global last_message_time
    # TODO: Need Normal Mode logic? @Ethan
    # Wait until `message_spacing` seconds after the last received message
    while True:
        while time.time() - last_message_time < config['aprs']['message_spacing']:
            time.sleep(1)
        last_message_time = time.time()

        ser.write((msg + '\n').encode("utf-8"))  # Send the message

        time.sleep(1)


def listen(ser):
    """
    Read messages from serial. If a command is received, send it to `command_ingest`
    """
    global last_message_time, last_telem_time
    while True:
        line = b''
        while not line.endswith(b'\n'):  # While EOL hasn't been sent
            logger.debug("GOT SOMETHING")
            res = ser.readline()
            line += res
        line = line.decode('utf-8')
        # Update last message time
        last_message_time = time.time()
        if line[0:2] == 'T#':  # Telemetry Packet: APRS special case
            last_telem_time = time.time()
            logger.debug('APRS telemetry heartbeat received')
            continue  # Don't parse telemetry packets

        # Dispatch command
        parsed = parse_aprs_packet(line)
        command_ingest.dispatch(parsed)


def parse_aprs_packet(packet: str) -> str:
    """
    Given a raw radio packet, strip the APRS junk off of it and make it into pure data.
    :param packet: Input data packet to process.
    :return: The pure data with all APRS wrappers removed.
    """
    raw_packet = str(packet)
    logger.debug("From APRS: " + raw_packet)
    header_index = raw_packet.find(':')
    if header_index == -1:
        logger.error("Incomplete APRS header!")
        return ""  # TODO: make sure this is what we want to do.
    header = raw_packet[:header_index]
    logger.debug("header: " + header)
    data = raw_packet[header_index + 1:]

    if len(data) == 0:
        logger.warning("Empty packet body!")
        # return ""

    logger.debug("Body: " + data)
    return data
    # command_ingest.dispatch(data)


def start():

    # Opens the serial port for all methods to use with 19200 baud
    ser = serial.Serial(config['aprs']['serial_port'], 19200)

    # Create all the background threads
    t1 = ThreadHandler(target=partial(listen),
                       name="aprs-listen", parent_logger=logger)

    # Start the background threads
    t1.start()
