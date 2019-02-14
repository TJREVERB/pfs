import threading
from functools import partial

import serial
import time
import logging

from core import config
from . import command_ingest
from . import eps
from .command_ingest import command
from helpers.threadhandler import ThreadHandler
from helpers.helpers import is_simulate

debug = True

global ser

# Initialize global variables
logger = logging.getLogger("IRIDIUM")


def write_to_serial(cmd):
    """
    Write a command to the serial port.

    :param cmd: Command to write
    """

    # Append EOL if it isn't present alredy
    if cmd[-2:] != '\r\n':
        cmd += '\r\n'

    ser.write(cmd.encode('UTF-8'))  # Encode the message with utf-8

    response = ""  # Received response
    while "OK" not in response:  # Wait to get the 'OK' from the Iridium
        response += ser.readline().decode('UTF-8')  # Append contents of serial
    # Filter out the newline and the 'OK'
    response.replace("\r\n", "").replace("OK", "")

    ser.flush()  # Flush the serial

    return response


def check():
    write_to_serial("AT")  # Test the Iridium

    signalQuality = write_to_serial('AT+CSQ')  # Show signal quality

    write_to_serial("AT+SBDMTA=0")

    response = write_to_serial("AT+SBDREG?").split(":")

    if response != 2:
        write_to_serial("AT+SBDREG")  # Retry the SBD Network Registration


def listen():
    write_to_serial("AT+SBDMTA=1")
    signalStrength = 0
    ringSetup = 0
    iteration = 0
    while ringSetup != 2:
        print("Just inside ring setup loop")
        ring = ser.readline().decode('UTF-8')
        print(ring)
        print("if SBDRING next")
        if "SBDRING" in ring:
            bytesLeft = 1
            ser.timeout = 120
            while bytesLeft != 0:
                print("checking bytes left")
                write_to_serial("AT+SBDIXA")
                resp = "A"
                while len(resp) < 2:
                    print("response length loop")
                    test = ser.readline().decode('UTF-8')
                    resp = test.split(': ')

                try:
                    print("splitting response")
                    resp = resp[1].split(', ')
                except:
                    print("index out of bounds exception \r\n closing program")
                    exit(-1)
                bytesLeft = int(resp[0])

            write_to_serial("AT+SBDRT")
            print("About to show message")
            while True:
                try:
                    print(ser.readline().decode('UTF-8').split(":")[1])

                    print("done")
                    break
                except:
                    continue
            ringSetup = 0


def send(message):
    # Try to send until it sends
    startTime = time.time()
    alert = 2
    while alert == 2:
        # Get last known signal strength
        write_to_serial("AT+CSQF")

        # Prepare message
        write_to_serial("AT+SBDWT=" + message)

        # Send message
        response = write_to_serial("AT+SBDI").replace(",", " ")

        startTime = time.time()
        currTime = startTime

        while len(response) > 0 and len(response) <= 2:
            response = write_to_serial("AT+SBDI").replace(",", " ")
            curTime = time.time()
            if (curTime - startTime) > 30:
                break
        try:
            alert = int(response[1])
        except:
            continue


def start():
    global ser

    # Opens the serial port for all methods to use with 19200 baud
    ser = serial.Serial(
        config['iridium']['serial_port'], baudrate=19200, timeout=15)
    ser.flush()  # clean house before starting

    # Create all the background threads
    # t1 = ThreadHandler(target=partial(listen),name="iridium-listen", parent_logger=logger)
    # no threads it breaks serial

    check()

    # Start the threads
    # t1.start() threads break serial

    time.sleep(1)
    send("TEST")
