import logging
import threading
import time
from functools import partial

import serial

from core import config
from helpers.threadhandler import ThreadHandler

debug = True

ser = None

# Initialize global variables
logger = logging.getLogger("IRIDIUM")
read_lock = threading.Lock()


def write_to_serial(command: str) -> (str, bool):
    """
    Write a command to the serial port.

    :param command: Command to write
    :return: Tuple consisting of (response text, boolean if error or not)
    """

    # Remove unnecessary newlines that cut off the full command
    command = command.replace("\r\n", "")
    # Add the newline character to the end of the command
    command = command + "\r\n"

    # Encode the message with utf-8, write to serial
    ser.write(command.encode('UTF-8'))

    response = ""  # Received response
    read_lock.acquire()
    while ("OK" or "ERROR") not in response:  # Wait to get the 'OK' or 'ERROR' from Iridium
        response += ser.readline().decode('UTF-8')  # Append contents of serial
    read_lock.release()

    # Determine if an "OK" or an "ERROR" was received
    if "OK" in response:  # "OK"
        response = response.replace("OK", "").strip()
        ser.flush()  # Flush the serial
        return response, True
    else:  # "ERROR"
        response = response.replace("ERROR", "").strip()
        ser.flush()  # Flush the serial
        return response, False


def wait_for_signal() -> None:
    """
    Wait for the Iridium to establish a connection with the constellation.
    """
    response = 0
    while response == 0:
        response = int(write_to_serial("AT+CSQ")[0])


def check(num_checks: int) -> bool:
    """
    Check that the Iridium works and is registered.
    :param num_checks: Number of times to check if the Iridium is registered (before it returns)
    :return: True if check was successful, False if not
    """

    write_to_serial("AT")  # Test the Iridium

    wait_for_signal()
    # Get the current registration status of the Iridium
    # Return OK and end lines when they should be removed in write_to_serial
    response = int(write_to_serial("AT+SBDREG?")[0].split(":")[1])

    # `response` should be 2, which means the Iridium is registered
    while num_checks > 0:  # Recheck the Iridium for `num_checks` number of times
        if response == 2:  # Check succeeded
            return True
        else:  # Check failed, retry
            response = int(write_to_serial("AT+SBDREG?")[0].split(":")[1])
            num_checks -= 1
    return False  # Check failed all times, return False


def listen():
    # Turn SBD ring alerts on
    write_to_serial("AT+SBDMTA=1")

    while True:  # Continuously listen for rings
        # Wait for `read_lock` to be released, implies loop is run every 5 seconds minimum
        acquired_read_lock = read_lock.acquire(timeout=5)
        if acquired_read_lock:
            ring = ser.readline().decode('UTF-8')
            read_lock.release()
            if "SBDRING" in ring:
                retrieve()


def retrieve():
    # FIXME: This method is temporarily holding the code that was previously in listen()

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
    write_to_serial("AT+SBDMTA=0")


def send(message: str) -> bool:
    """
    Send a message using the Iridium network.
    :param message: The message to send in plain text
    :return: True if message was sent, False if not
    """

    wait_for_signal()
    # Prepare message
    response_write = write_to_serial("AT+SBDWT=" + message)
    if not response_write[1]:  # Message write timed out
        return False

    wait_for_signal()
    # Send message
    response_sbdi = write_to_serial("AT+SBDI")
    if not response_sbdi[1]:
        return False

    response_sbdi_array = response_sbdi[0].split(
        ":")[1].strip().split(",")  # Array of SBDI response

    if response_sbdi_array[0] == 2:  # Index 0 holds the success code
        return True
    else:
        return False


def start():
    global ser

    # Opens the serial port for all methods to use with 19200 baud
    ser = serial.Serial(config['iridium']['serial_port'], baudrate=19200)
    # Clean serial port before proceeding
    ser.flush()

    check(5)  # Check that the Iridium (check 5 times)
    logging.debug("Check successful")

    listen_thread = ThreadHandler(target=partial(
        listen), name="iridium-listen", parent_logger=logger)
    listen_thread.start()
