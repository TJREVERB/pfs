import logging
import os
import threading
import time
from functools import partial
from subprocess import call
from threading import Thread

import sys
import queue
import pynmea2
import serial

from core import config
from . import aprs

from .threadhandler import ThreadHandler

logger = logging.getLogger("GPS")

lat = -1.0
lon = -1.0
alt = -1.0

#time = datetime.time(0, 0, 0)

# EDIT THIS TO WORK WITH GPS
def sendgpsthruaprs(givenarg):
    global cached_nmea_obj
    if cached_nmea_obj is not None:
        aprs.enqueue(
            str(cached_nmea_obj.altitude) + str(cached_nmea_obj.altitude_units) + str(cached_nmea_obj.lat) + str(
                cached_nmea_obj.lat_dir) + str(cached_nmea_obj.lon) + str(cached_nmea_obj.lon_dir))


def queryfield(field):
    send("log " + str(field))


def querygps():
    global cached_nmea_obj

    return cached_nmea_obj


def querypastgps(index):
    # RETURN A PAST GPS COORDINATE BY INDEX
    # REFERENCE OWN GPS LOGS
    return


def passivegps():
    # PASSIVELY UPDATE cached_nmea_obj According to gps period
    global cached_nmea_obj, gpsperiod
    while True:
        time.sleep(gpsperiod)
        cached_nmea_obj = getsinglegps()


def getsinglegps():
    # EXAMPLE METHOD THAT STILL NEEDS TO BE FLESHED OUT
    # AS YOU CAN SEE THERRE'S STILL A TON TO DO
    send("ANTENNAPOWER ON")
    # pseudo
    # checkifgpslock()
    gpsdata = recordgps()
    log(gpsdata)
    send("ANTENNAPOWER OFF")
    return gpsdata
    # end pseudo


def parsegps(bytes):
    str(bytes)


def send(msg):
    msg += "\n"
    ser.write(msg.encode("utf-8"))


def listen():
    while True:
        time.sleep(2)
        raise Exception("EX")
        # Read in a full message from serial
        line = ser.readline()
        # Dispatch command
        parse_gps_packet(line)
        # logger.info(line)
        # print(rr)
        # log('GOT: '+rr)



def parse_gps_packet(packet):
    global cached_nmea_obj
    packet = str(packet)[2:-5]
    logger.info(packet)
    # packet = packet[]
    logger.debug(packet[0:6])
    if packet[0:6] == '$GPGGA':
        # logger.info('POS UPDATE')
        nmea_obj = pynmea2.parse(packet)
        cached_nmea_obj = nmea_obj
        # ANUP FIX THE 3 LINES BELOW. cached_nmea_obj.lat instead?? - Shihao
        # lat = pynmea2.lat
        # lon = pynmea2.lon
        # alt = pynmea2.altitude
        # updateTime(pynmea2.time)


def gpsbeacon():
    global cached_nmea_obj
    while True:
        time.sleep(gpsperiod)
        if cached_nmea_obj is not None:
            aprs.enqueue(
                str(cached_nmea_obj.altitude) + str(cached_nmea_obj.altitude_units) + str(cached_nmea_obj.lat) + str(
                    cached_nmea_obj.lat_dir) + str(cached_nmea_obj.lon) + str(cached_nmea_obj.lon_dir))
    # if packet[]

# Update system time based on the given time
# time is a time object in UTC time
def updateTime(time):
    os.system('date -s "' + str(time.hour) + ':' + str(time.minute) + ':' + str(time.second) + ' UTC"')

def keyin():
    while (True):
        # GET INPUT FROM YOUR OWN TERMINAL
        # TRY input("shihaoiscoolforcommentingstuff") IF raw_input() doesn't work
        in1 = input("Type Command: ")
        send(in1)
        # send("TJ" + in1 + chr(sum([ord(x) for x in "TJ" + in1]) % 128))

def stop(self):
    self.stopped = True

def on_startup():
    # GLOBAL VARIABLES ARE NEEDED IF YOU "CREATE" VARIABLES WITHIN THIS METHOD
    # AND ACCESS THEM ELSEWHERE
    global gpsperiod, t1, ser, logfile, tlt, cached_nmea_obj
    # cached_nmea_obj = (None,None)
    cached_nmea_obj = None
    gpsperiod = 10
    serialPort = config['gps']['serial_port']
    # REPLACE WITH COMx IF ON WINDOWS
    # REPLACE WITH /dev/ttyUSBx if 1 DOESNT WORK
    # serialPort = "/dev/ttyS3"
    # OPENS THE SERIAL PORT FOR ALL METHODS TO USE WITH 19200 BAUD
    ser = serial.Serial(serialPort, 9600)

    testT = ThreadHandler(target=lambda: listen(), parent_logger=logger, auto_restart=False)
    testT.start()

    time.sleep(5)

    testT.resume()

    time.sleep(5)

    testT.pause()
    #
    # listenT = Thread(target=threadhandler(listen, parent_logger=logger), name="listen", daemon=True)
    # listenT.start()


    # gpsbeaconT = Thread(target=threadhandler(gpsbeacon, parent_logger=logger), name="gpsbeacon", daemon=True)
    # gpsbeaconT.start()

    tlt = time.localtime()
    # Open the log file
    log_dir = os.path.join(config['core']['log_dir'], 'gps')
    filename = 'gps' + '-'.join([str(x) for x in time.localtime()[0:3]])
    # ensure that the GPS log directory exists
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    logfile = open(os.path.join(log_dir, filename + '.txt'), 'a+')

    log('RUN@' + '-'.join([str(x) for x in tlt[3:5]]))

    send('echo off')
    send('unlogall')
    send('antennapower on')
    send('log gpgga ontime 8')
    # send("ANTENNAPOWER OFF")


# I NEED TO KNOW WHAT NEEDS TO BE DONE IN NORMAL, LOW POWER, AND EMERGENCY MODES
def enter_normal_mode():
    # UPDATE GPS MODULE INTERNAL COORDINATES EVERY 10 MINUTES
    update_internal_coords()
    # time.sleep(600)


def enter_low_power_mode():
    # UPDATE GPS MODULE INTERNAL COORDINATES EVERY HOUR
    update_internal_coords()
    # time.sleep(3600)


def enter_emergency_mode():
    # ALL GPS FUNCTIONS OFF. LOWEST POWER POSSIBLE
    call("unlog")  # I don't know any other off functions - comment some here or message me (Rishabh) some on slack


# USE THIS LOG FUNCTION
def log(msg):
    global logfile
    logfile.write(msg + '\n')
    logfile.flush()


if __name__ == '__main__':

    t2 = Thread(target=keyin, args=())
    t2.daemon = True
    t2.start()
    while True:
        time.sleep(1)
