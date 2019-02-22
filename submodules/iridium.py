import logging
import time

import serial

from core import config

debug = True

global ser

# Initialize global variables
logger = logging.getLogger("IRIDIUM")


def write_to_serial(cmd):
    """
    Write a command to the serial port.

    :param cmd: Command to write
    :return: Tuple consisting of (response text, boolean if error or not)
    """

    # Append EOL if it isn't present alredy
    if cmd[-2:] != '\r\n':
        cmd += '\r\n'

    ser.write(cmd.encode('UTF-8'))  # Encode the message with utf-8

    response = ""  # Received response
    while ("OK" or "ERROR") not in response:  # Wait to get the 'OK' or 'ERROR' from Iridium
        response += ser.readline().decode('UTF-8')  # Append contents of serial

    # Determine if an "OK" or an "ERROR" was received
    if "OK" in response:
        response.replace("OK", "")
        response.replace("/r/n", "")
        ser.flush()  # Flush the serial
        return response, True
    else:
        response.replace("ERROR", "").strip()
        ser.flush()  # Flush the serial
        return response, False


def check(numChecks):
    """
    Check that the Iridium works and is registered
    :param numChecks: Number of times to check if the Iridium is registered
    :return: True if check was successful, False if not
    """

    write_to_serial("AT")  # Test the Iridium

    signalQuality = write_to_serial('AT+CSQ')  # Get current signal quality
    logger.debug(signalQuality[0])

    # Disable SBD Ring Alerts to get registration status
    write_to_serial("AT+SBDMTA=0")

    # Get the current registration status of the Iridium
    response = int(write_to_serial("AT+SBDREG?")[0].split(":")[1]) # Returning OK instead of 2, add check for these types of commands in write_to_serial

    # `response` should be 2, which means the Iridium is registered
    while numChecks > 0:  # Recheck the Iridium for `numChecks` number of times
        if response == 2:  # Check succeeded
            return True
        else:  # Check failed, retry
            response = write_to_serial("AT+SBDREG")[0]
            numChecks -= 1
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
    # Clean serial port before proceeding
    ser.flush()

    check(5)  # Check that the Iridium works 5 times

    # Create all the background threads
    # t1 = ThreadHandler(target=partial(listen),name="iridium-listen", parent_logger=logger)
    # no threads recommended it breaks serial

    # Start the threads
    # t1.start() threads break serial

    time.sleep(1)
    send("TEST")
