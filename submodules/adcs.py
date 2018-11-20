import logging
import os
import time
from functools import partial

from core import config

from core.threadhandler import ThreadHandler

logger = logging.getLogger("ADCS")


def send(msg):
    msg += "\n"
    ser.write(msg.encode("utf-8"))


def listen():
    while True:
        # Read in a full message from serial
        time.sleep(1);
        # Dispatch command
        # logger.info(line)
        # print(rr)
        # log('GOT: '+rr)


def updateVals(msg):
    # saves velocity data from gps
    global velocity_data
    velocity_data = msg


def keyin():
    while (True):
        # GET INPUT FROM YOUR OWN TERMINAL
        # TRY input("shihaoiscoolforcommentingstuff") IF raw_input() doesn't work
        in1 = input("Type Command: ")
        send(in1)
        # send("TJ" + in1 + chr(sum([ord(x) for x in "TJ" + in1]) % 128))


def on_startup():
    # GLOBAL VARIABLES ARE NEEDED IF YOU "CREATE" VARIABLES WITHIN THIS METHOD
    # AND ACCESS THEM ELSEWHERE
    global t1, logfile, tlt
    # cached_nmea_obj = (None,None)

    # serialPort = config['adcs']['serial_port']
    # REPLACE WITH COMx IF ON WINDOWS
    # REPLACE WITH /dev/ttyUSBx if 1 DOESNT WORK
    # serialPort = "/dev/ttyS3"
    # OPENS THE SERIAL PORT FOR ALL METHODS TO USE WITH 19200 BAUD
    # ser = serial.Serial(serialPort, 9600)
    # CREATES A THREAD THAT RUNS THE LISTEN METHOD
    t1 = ThreadHandler(target=partial(listen), name="adcs-listen", parent_logger=logger)
    t1.start()

    tlt = time.localtime()

    # Open the log file
    log_dir = os.path.join(config['core']['log_dir'], 'adcs')
    filename = 'adcs' + '-'.join([str(x) for x in time.localtime()[0:3]])
    # ensure that the GPS log directory exists
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    logfile = open(os.path.join(log_dir, filename + '.txt'), 'a+')

    log('RUN@' + '-'.join([str(x) for x in tlt[3:5]]))

    # send("ANTENNAPOWER OFF")


# I NEED TO KNOW WHAT NEEDS TO BE DONE IN NORMAL, LOW POWER, AND EMERGENCY MODES
def enter_normal_mode():
    # UPDATE GPS MODULE INTERNAL COORDINATES EVERY 10 MINUTES
    # time.sleep(600)
    pass


def enter_low_power_mode():
    # UPDATE GPS MODULE INTERNAL COORDINATES EVERY HOUR
    # time.sleep(3600)
    pass


def enter_emergency_mode():
    pass


# TODO fix this
def get_pry():
    return (-1, -1, -1)


def get_mag():
    return (-1, -1, -1)


def get_abs():
    return (-1, -1, -1)


def can_TJ_be_seen():
    return True  # fix me!


# USE THIS LOG FUNCTION
def log(msg):
    global logfile
    logfile.write(msg + '\n')
    logfile.flush()


if __name__ == '__main__':
    t2 = ThreadHandler(target=partial(keyin), name="adcs-keyin", parent_logger=logger)
    t2.daemon = True
    t2.start()
    while True:
        time.sleep(1)
