import logging
import threading

import serial

from core.mode import Mode

from core import config
from submodules import command_ingest

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
        response = int(write_to_serial("AT+CSQ")[0].split(":")[1])


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


def listen() -> None:
    """
    Listen for an SBD ring.
    If a ring is present, retrieve the message, and dispatch it to *command_ingest.*
    This function is meant to be run in a Thread.
    """

    # Turn SBD ring alerts on
    write_to_serial("AT+SBDMTA=1")

    while True:  # Continuously listen for rings
        # Wait for `read_lock` to be released, implies loop is run every 5 seconds minimum
        while state == Mode.NORMAL:
            acquired_read_lock = read_lock.acquire(timeout=5)
            if acquired_read_lock:
                ring = ser.readline().decode('UTF-8')
                read_lock.release()
                logger.debug("Got SBDRING")
                if "SBDRING" in ring:
                    message = retrieve()
                    logger.debug(f"Message was {message}")
                    if message:  # Evaluates to True if message not empty
                        logger.debug(message)
                        command_ingest.dispatch(message)
        time.sleep(1)


def retrieve() -> str:
    """
    Retrieve the content of a message that is Mobile Terminated (MT).
    :return: Text content of the message, empty string if failed or no message to retrieve
    """

    wait_for_signal()

    # "Sync" with the GSS, retrieving and sending messages
    sync_resp = write_to_serial("AT+SBDIXA")[0]
    sync_resp_list = sync_resp.strip(",")

    if sync_resp_list[2] == 1:  # Message successfully received
        message = write_to_serial("AT+SBDRT")
        return message[0]  # Return the actual message content
    else:
        return ""  # Return nothing; either there was no message or retrieval failed


@command("iridium_echo", str)
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
    logger.debug("At start of iridium")
    global ser, state

    state = None

    # Opens the serial port for all methods to use with 19200 baud
    ser = serial.Serial(config['iridium']['serial_port'],baudrate=19200, timeout=30)
    # Clean serial port before proceeding
    ser.flush()

    check(5)  # Check that the Iridium (check 5 times)
    logger.debug("Check successful")

    listen_thread = ThreadHandler(target=partial(listen), name="iridium-listen", parent_logger=logger)
    listen_thread.start()


def enter_normal_mode():
    global state
    state = Mode.NORMAL


def enter_low_power_mode():
    global state
    state = Mode.LOW_POWER


def enter_emergency_mode():
    global state
    state = Mode.EMERGENCY
