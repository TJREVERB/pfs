import logging
import time

import serial

from core import config

debug = True

global ser

# Initialize global variables
logger = logging.getLogger("IRIDIUM")


def write_to_serial(command):
    """
    Write a command to the serial port.

    :param command: Command to write
    :return: Tuple consisting of (response text, boolean if error or not)
    """

    # Append EOL if it isn't present already
    if command[-2:] != '\r\n':
        command += '\r\n'

    ser.write(command.encode('UTF-8'))  # Encode the message with utf-8

    response = ""  # Received response
    while ("OK" or "ERROR") not in response:  # Wait to get the 'OK' or 'ERROR' from Iridium
        response += ser.readline().decode('UTF-8')  # Append contents of serial

    # Determine if an "OK" or an "ERROR" was received
    if "OK" in response:
        response = response.replace("OK", "").strip()
        ser.flush()  # Flush the serial
        return response, True
    else:
        response = response.replace("ERROR", "").strip()
        ser.flush()  # Flush the serial
        return response, False


def check(num_checks):
    """
    Check that the Iridium works and is registered
    :param num_checks: Number of times to check if the Iridium is registered
    :return: True if check was successful, False if not
    """

    write_to_serial("AT")  # Test the Iridium

    signalQuality = write_to_serial('AT+CSQ')  # Get current signal quality
    logger.debug(signalQuality[0])

    # Disable SBD Ring Alerts to get registration status
    write_to_serial("AT+SBDMTA=0")

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
    """
    Send a message using the Iridium network.
    :param message: The message to send in plain text
    :return:
    """

    alert = 2
    while alert == 2:
        # Get last known signal strength
        write_to_serial("AT+CSQ")

        # Prepare message
        response_write = write_to_serial("AT+SBDWT=" + message)  # Message write timed out
        if not response_write[1]: return False

        # Send message
        response_sbdi = write_to_serial("AT+SBDI")
        if not response_sbdi[1]: return False
        response_sbdi_array = response_sbdi[0].split(":")[1].strip().split(",")  # Array of SBDI response

        if response_sbdi_array[0] == 2:
            return True
        else:
            return False


def start():
    global ser

    # Opens the serial port for all methods to use with 19200 baud
    ser = serial.Serial(
        config['iridium']['serial_port'], baudrate=19200, timeout=120)
    # Clean serial port before proceeding
    ser.flush()

    check(5)  # Check that the Iridium (check 5 times)

    # Create all the background threads
    # t1 = ThreadHandler(target=partial(listen),name="iridium-listen", parent_logger=logger)
    # no threads recommended it breaks serial

    # Start the threads
    # t1.start() threads break serial

    time.sleep(1)
