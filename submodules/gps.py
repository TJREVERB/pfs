import logging
import os
import pty
import sys
import threading
import time
from functools import partial
import RPi.GPIO as GPIO
import base64
import struct
import datetime
from collections import deque
import pynmea2
import serial

from core import config
from helpers.helpers import is_simulate
from helpers.threadhandler import ThreadHandler

from submodules import telemetry
logger = logging.getLogger("GPS")

signal_lock = threading.Lock()
ser_master, ser_slave = pty.openpty()  # Serial ports for when in simulate mode


# Return a GPS position packet as returned by gpgga


def get_position_packet():
    """
    Starts a gpgga log job, parses and caches one reading
    :return: latitude,longitude,altitude, and time readings in dictionary format
    """
    global cached_nmea_obj
    send("log gpgga ontime 1")
    gps_packet = capture_packet('gps')
    logger.debug(gps_packet)
    gps_packet = parse_nmea_obj(gps_packet)
    cached_nmea_obj = gps_packet
    send("unlogall")
    return gps_packet


# Return a GPS velocity packet as returned by bestxyz
def get_velocity_packet():
    """
    Starts a bestxyz log job, parses and caches one reading
    :return: x/y/z velocity and position along with status code in dictionary format
    """
    global cached_xyz_obj
    send("log bestxyz ontime 1")
    time.sleep(1)
    # temp = ser.readline()[2:-5]
    # xyz_packet = ser.readline()[0:-5].decode("ascii")

    xyz_packet = capture_packet('vel')
    xyz_packet = parse_xyz_packet(xyz_packet)
    cached_xyz_obj = xyz_packet
    send("unlogall")
    return xyz_packet


# Return both the gps position and velocity packet
def record_gps():
    """
    Gets a single reading from the gps assuming gps is already on and initialized. Does not turn off gps
    :return: single dictionary of all readings
    """
    global cached_data_obj
    gps_packet = get_position_packet()
    xyz_packet = get_velocity_packet()

    data_obj = merge(gps_packet, xyz_packet)
    cached_data_obj = data_obj

    return data_obj


def getsinglegps():
    """
    Takes a single reading of all log jobs
    :return: latitude,longitude,altitude,x/y/z velocity and position, and status code in dictionary format
    """
    global cached_data_obj
    if not is_simulate('gps'):
        pass
    with signal_lock:
        # eps.pin_on("gps")
        t1.pause()
        send("unlogall")
        send("ANTENNAPOWER ON")
        send("ASSIGNALL AUTO")
        send("FIX AUTO")

        if not has_signal():
            wait_for_signal()

        gpsdata = record_gps()
        cached_data_obj = gpsdata
        send("ANTENNAPOWER OFF")
        # eps.pin_off('gps')
        return gpsdata
    # end pseudo


def send(msg):
    """
    Write a message to serial.
    :param msg: Message to write to serial.
    """
    msg += "\n"
    ser.write(msg.encode("utf-8"))





def findnth(msg, val, n):  # parsing helper method
    """
    Finds the nth occurrence of a character in a string
    :param msg: full string to parse
    :param val: character to be found
    :param n: occurrence number
    :return: nth occurrence of val in msg
    """
    parts = msg.split(val, n + 1)
    if len(parts) <= n + 1:
        return -1
    return len(msg) - len(parts[-1]) - len(val)


def parse_xyz_packet(packet):
    """
    Parses a bestxyz line from the gps and returns data in a dictionary format
    :param packet: raw bestxyz gps line
    :return: dictionary of x/y/z velocity and position along with status code
    """
    logger.info("parsing xyz")
    result = {}

    # specific message @ https://docs.novatel.com/OEM7/Content/PDFs/OEM7_Commands_Logs_Manual.pdf
    # pg.434 table.73
    # status messages for bestxyz reliability (not 0 is bad)
    status_code = {'SOL_COMPUTED': 0, 'INSUFFICIENT_OBS': -1, 'NO_CONVERGENCE': 2, 'SINGULARITY': 3, 'COV_TRACE': 4,
                   'TEST_DIST': 5, 'COLD_START': 6, 'V_H_LIMIT': 7, 'VARIANCE': 8, 'RESIDUALS': 9,
                   'INTEGRITY_WARNING': 13, 'PENDING': 18, 'INVALID_FIX': 19, 'UNAUTHORIZED': 20, 'INVALID_RATE': 22}

    result['position_status'] = status_code[packet[:findnth(packet, ' ', 0)]]
    result['x_pos'] = float(packet[findnth(packet, ' ', 1) + 1:findnth(packet, ' ', 2)])
    result['y_pos'] = float(packet[findnth(packet, ' ', 2) + 1:findnth(packet, ' ', 3)])
    result['z_pos'] = float(packet[findnth(packet, ' ', 3) + 1:findnth(packet, ' ', 4)])

    packetv = packet[findnth(packet, ' ', 7) + 1:]

    result['velocity_status'] = status_code[packetv[:findnth(packetv, ' ', 0)]]
    result['x_vel'] = float(packetv[findnth(packetv, ' ', 1) + 1:findnth(packetv, ' ', 2)])
    result['y_vel'] = float(packetv[findnth(packetv, ' ', 2) + 1:findnth(packetv, ' ', 3)])
    result['z_vel'] = float(packetv[findnth(packetv, ' ', 3) + 1:findnth(packetv, ' ', 4)])

    return result


def parse_nmea_obj(packet):
    """
    Parses a gpgga line from the gps and returns data in a dictionary format using pynmea2 and the NMEA standard
    :param packet: raw gpgga gps line
    :return: dictionary of latitude,longitude,altitude, and time
    """
    logger.debug("parsing nmea")
    if packet is not None:
        update_time(packet.timestamp)
        return {'lat': packet.lat, 'lon': packet.lon, 'alt': packet.altitude, 'alt_unit': packet.altitude_units,
                'lon_dir': packet.lon_dir, 'lat_dir': packet.lat_dir, 'time': packet.timestamp}


def get_data():
    """
    Returns the cached dictionary of all the data
    :return: latest data packet in dictionary form
    """
    return cached_data_obj


def capture_packet(packet_type):
    """
    Ensures a data packet is read from the gps. Excludes all incorrect data
    :param packet_type: either 'gps' or 'vel' to return either a gps or velocity packet
    :return: genuine packet of data
    """
    acquired = False
    while not acquired:
        try:
            packet = ser.readline()
            packet = packet.decode("ascii")
            if packet[0:4] == '[COM':
                packet = packet[6:]

            packet = packet[0:-5]

            if packet_type == 'gps':
                try:
                    nmea_packet = pynmea2.parse(packet)
                except pynmea2.nmea.ParseError:
                    logger.error("NMEA PARSING ERROR")
                    acquired = False
                    continue
                return nmea_packet

            if packet_type == 'vel':
                if packet[0:8] == '<BESTXYZ':
                    xyz_packet = ser.readline()[0:-5].decode("ascii")
                    return xyz_packet[6:-33]
                else:
                    logger.error(packet)
                    acquired = False
                    continue

        except serial.SerialException:
            acquired = False
            continue


def merge(x, y):  # parsing helper method
    """
    Merges two dictionaries
    :param x: First dictionary
    :param y: Second dictionary
    :return: combined dictionary of x and y with the values in x preceding values in y
    """
    logger.debug("merging")
    x.update(y)
    return x


def update_time(new_time):
    """
    Update system time based on the given time.
    :param new_time: A `time` object in UTC format.
    """
    if new_time is not None:
        os.system('date -s "' + str(new_time.hour) + ':' +
                  str(new_time.minute) + ':' + str(new_time.second) + ' UTC"')
        logger.debug("system time updated")
    else:
        logger.error("system time not updated.")


def keyin():
    """
    Takes in input and sends to gps
    """
    while True:
        # Use `raw_input()` if working with Python2
        in1 = input("Type Command: ")
        send(in1)
        # send("TJ" + in1 + chr(sum([ord(x) for x in "TJ" + in1]) % 128))


def thread(args1, stop_event, queue_obj):
    print("starting thread")
    stop_event.wait(10)
    if not stop_event.is_set():
        try:
            raise Exception("signal!")
        except Exception:
            queue_obj.put(sys.exc_info())
    pass


# TODO TEST IF WORKS
def get_points(period):
    """
    Returns a list of multiple dictionaries defined by period. Each dictionary is a singular reading from the gps
    :param period: Amount of time in seconds of data needed
    :return: list of dictionaries of all data recorded
    """
    # eps.pin_on('gps')
    with signal_lock:
        logger.info("PARSING " + str(period) + " POINTS")
        send("ANTENNAPOWER ON")
        send("ASSIGNALL AUTO")
        send("FIX AUTO")
        wait_for_signal()
        runtime = 0
        points = []

        while runtime != period:
            packet = record_gps()
            if point_is_good(packet):
                telemetry_send(packet)
                points.append(packet)
                runtime += 1

        cache.append(points)
        send("unlogall")
        # eps.pin_off('gps')


def get_cache():
    return cache


# TODO TEST IF WORKS
def update_cache():
    """
    Updates the system cache of gps data
    """
    logger.info("UPDATING CACHE STORAGE")
    cache.append(get_points(gpsperiod))
    logger.debug(cache)


def start():
    """
    Initializes all variables and starts all thread on boot
    :return:
    """
    global t1, t2, ser, cached_nmea_obj, cached_xyz_obj, cached_data_obj, cache, gpsperiod
    # cached_nmea_obj = (None,None)
    cached_nmea_obj = None  # cached lat/lon/alt/gps object
    cached_xyz_obj = None  # cached velocity object
    cached_data_obj = None  # final data packet
    cache = deque([],2)  # deque of (lists of dictionaries -returned by get k points)

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(26, GPIO.IN)

    # TODO UPDATE FOR ACTUAL VALUE
    updateinterval = 10  #FIXME val = 90 minutes in seconds
    gpsperiod = 10 #FIXME val = 300

    # Opens the serial port for all methods to use with 19200 baud
    if is_simulate('gps'):
        s_name = os.ttyname(ser_slave)
        ser = serial.Serial(s_name, 19200)
        logger.info("Serial started on " + ser.name)
    else:
        ser = serial.Serial(config['gps']['serial_port'], 9600, timeout=10)
        # eps.pin_on('gps')

    # REPLACE WITH /dev/ttyUSBx if 1 DOESNT WORK
    # serialPort = "/dev/ttyS3"

    t1 = ThreadHandler(target=partial(get_points(gpsperiod)), name="gps-listen",
                       parent_logger=logger)  # thread for parsing and caching log packets
    t2 = threading.Timer(float(updateinterval), update_cache)

    # t2.start()
    t2.start()
    t3.start()


def telemetry_send():
    gps_packet = getsinglegps()
    lat = gps_packet['lat']
    lon = gps_packet['lon']
    alt = gps_packet['alt']
    t = gps_packet['time']
    t = t.replace(tzinfo=datetime.timezone.utc).timestamp()

    packet = "G"
    packet += base64.b64encode(struct.pack('d', t)).decode("UTF-8")
    packet += base64.b64encode(struct.pack('fff', lat, lon, alt)).decode("UTF-8")

    telemetry.enqueue_submodule_packet(packet)




def has_signal():
    return GPIO.input(26) == 1

def wait_for_signal():  # Temporary way of waiting for signal lock by waiting for an actual reading from gpgga log
    """
    Continuously parses a gpgga log until signal lock.
    :return:
    """

    logger.info("WAITING FOR GPS LOCK")
    send("ANTENNAPOWER ON")
    send("ASSIGNALL AUTO")
    send("log gpgga ontime 1")
    line = b''

    acquired = False
    while not acquired:
        if GPIO.input(26) == 1:
            logger.info("GPS LOCK")
            acquired = True
            return
        else:
            continue


def start_loop():
    """
    Sends initial commands to gps to properly begin all log jobs
    :return:
    """
    global t1
    send('ECHO OFF')  # unnecessary for a headless system
    send('unlogall')  # stops all previous log jobs
    send('ANTENNAPOWER ON')  # ensures power is supplied to the antenna
    # assigns all gps systems to an automatic configuration
    send('ASSIGNALL AUTO')
    send('FIX AUTO')  # ensures bestxyz readings are accurate
    wait_for_signal()
    send('log gpgga ontime 5')  # starts to log gpgga every 5 seconds
    send('log bestxyz ontime 5')  # starts to log bestxyz every 5 seconds
    t1.start()  # start parsing and caching


# TODO: Need to know what needs to be done in normal, low power, and emergency modes.
def enter_normal_mode():
    # UPDATE GPS MODULE INTERNAL COORDINATES EVERY 10 MINUTES
    # update_internal_coords() IF THIS METHOD IS NECESSARY MESSAGE ME(Anup)
    # time.sleep(600)
    if not is_simulate('gps'):
        pass
    # eps.pin_on("gps")
    start_loop()


def enter_low_power_mode():
    # UPDATE GPS MODULE INTERNAL COORDINATES EVERY HOUR
    # update_internal_coords() IF THIS METHOD IS NECESSARY MESSAGE ME(Anup)
    # time.sleep(3600)
    pass


def enter_emergency_mode():
    # ALL GPS FUNCTIONS OFF. LOWEST POWER POSSIBLE
    send('UNLOGALL')
    send('ANTENNAPOWER OFF')
    send('ASSIGNALL IDLE')


if __name__ == '__main__':
    t3 = ThreadHandler(target=partial(
        keyin), name="gps-keyin", parent_logger=logger)
    t3.start()

    while True:
        time.sleep(1)
