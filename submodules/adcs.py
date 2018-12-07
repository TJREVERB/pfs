import logging
import os
import time
from functools import partial

from core import config

from helpers.threadhandler import ThreadHandler
from submodules.aprs import ser  # Resolve IDE errors about not finding serial

logger = logging.getLogger("ADCS")


def send(msg):
    """
    Write a message to serial.
    :param msg: Message to write to serial.
    """
    msg += "\n"
    ser.write(msg.encode("utf-8"))


def listen():
    """
    Read messages from serial.
    """
    while True:
        time.sleep(1)
        # Dispatch command
        # logger.info(line)
        # print(rr)
        # log('GOT: '+rr)


def updateVals(msg):
    """
    Saves and updates GPS values.
    :param msg: What to set as `velocity_data`.
    """
    global velocity_data
    velocity_data = msg


def keyin():
    while True:
        # Gets input from terminal
        in1 = input("Type Command: ")  # Use `raw_input()` if working with Python2

        send(in1)
        # send("TJ" + in1 + chr(sum([ord(x) for x in "TJ" + in1]) % 128))


def on_startup():
    # GLOBAL VARIABLES ARE NEEDED IF YOU "CREATE" VARIABLES WITHIN THIS METHOD
    # AND ACCESS THEM ELSEWHERE
    global t1, logfile, tlt

    # serialPort = config['adcs']['serial_port']
    # REPLACE WITH COMx IF ON WINDOWS
    # REPLACE WITH /dev/ttyUSBx if 1 DOESNT WORK
    # ser = serial.Serial(serialPort, 9600)

    # Run the `listen()` method
    t1 = ThreadHandler(target=partial(listen), name="adcs-listen", parent_logger=logger)
    t1.start()

    tlt = time.localtime()  # Get local time

    # Open the log file
    log_dir = os.path.join(config['core']['log_dir'], 'adcs')
    filename = 'adcs' + '-'.join([str(x) for x in time.localtime()[0:3]])

    # Ensure that the GPS log directory exists
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    logfile = open(os.path.join(log_dir, filename + '.txt'), 'a+')

    log('RUN@' + '-'.join([str(x) for x in tlt[3:5]]))

    # send("ANTENNAPOWER OFF")


# TODO: Need to know what needs to be done in normal, low power, and emergency modes.
def enter_normal_mode():
    """
    Enter normal power mode. Update the GPS module internal coordinates every **10** minutes.
    """
    # time.sleep(600)
    pass


def enter_low_power_mode():
    """
    Enter low power mode. Update the GPS module internal coordinates every **60** minutes.
    """
    # time.sleep(3600)
    pass


def enter_emergency_mode():
    """
    Enter emergency power mode.
    """
    pass


# TODO: Update these methods. Currently only holds placeholder methods.
def get_pry():
    return -1, -1, -1


def get_mag():
    return -1, -1, -1


def get_abs():
    return -1, -1, -1


def can_TJ_be_seen():
    return True  # TODO: Fix this method.


def log(msg):
    """
    Write a message to the ADCS logfile. Use this function to log messages.
    :param msg: Message to write to the logfile.
    """
    global logfile
    logfile.write(msg + '\n')
    logfile.flush()


if __name__ == '__main__':
    t2 = ThreadHandler(target=partial(keyin), name="adcs-keyin", parent_logger=logger)
    t2.daemon = True
    t2.start()

    # MAIN LOOP
    while True:
        time.sleep(1)
