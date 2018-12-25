import logging
import os
import sys
import time

import pynmea2
import serial

import os
import pty

from helpers.threadhandler import ThreadHandler
from helpers.helpers import is_simulate
from functools import partial

from submodules import aprs
from submodules import eps

from core import config

# from . import aprs
# from . import eps

logger = logging.getLogger("GPS")

ser_master, ser_slave = pty.openpty()  # Serial ports for when in simulate mode

# TODO: Edit this to work with GPS.
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
    """
    Retrieves a logged GPS coordinate by index. References GPS logs.
    :param index: Index of the desired GPS coordinate.
    :return: The past coordinate, located at `index`.
    """
    return


def passivegps():
    """
    Passively update `cached_nmea_obj` according to GPS period.
    """
    global cached_nmea_obj, gpsperiod
    while True:
        time.sleep(gpsperiod)
        cached_nmea_obj = getsinglegps()

# Return a GPS position packet as returned by gpgg
def get_position_packet():
    global cached_nmea_obj
    send("log gpgg ontime 1")
    time.sleep(1)
    gps_packet = ser.readline()[2:-5]
    send("unlogall")
    gps_packet = parse_nmea_obj(pynmea2.parse(gps_packet))
    update_time(gps_packet['time'])
    cached_nmea_obj = gps_packet
    return gps_packet

# Return a GPS velocity packet as returned by bestxyz
def get_velocity_packet():
    send("log bestxyz ontime 1")
    time.sleep(1)
    temp = ser.readline()[2:-5]
    xyz_packet = ser.readline()[2:-5]
    xyz_packet = parse_xyz_packet(xyz_packet)
    cached_xyz_obj = xyz_packet
    send("unlogall")
    return xyz_packet

# Return both the gps position and velocity packet
def recordgps():
    # global cached_nmea_obj, cached_xyz_obj
    # send("log gpgg ontime 1")
    # time.sleep(1)
    # gps_packet = ser.readline()[2:-5]
    # send("unlogall")
    # send("log bestxyz ontime 1")
    # time.sleep(1)
    # temp = ser.readline()[2:-5]
    # xyz_packet = ser.readline()[2:-5]
    # gps_packet = parse_nmea_obj(pynmea2.parse(gps_packet))
    # update_time(gps_packet['time'])
    # cached_nmea_obj = gps_packet
    # xyz_packet = parse_xyz_packet(xyz_packet)
    # cached_xyz_obj = xyz_packet
    # send("unlogall")
    gps_packet = get_position_packet()
    xyz_packet = get_velocity_packet()
    return merge(gps_packet, xyz_packet)


def getsinglegps():
    # EXAMPLE METHOD THAT STILL NEEDS TO BE FLESHED OUT
    # AS YOU CAN SEE THERRE'S STILL A TON TO DO
    global t1, t2, cached_data_obj
    eps.pin_on('gps')
    t1.pause()
    t3.pause()
    send("ANTENNAPOWER ON")
    send("FIX AUTO")
    wait_for_signal()
    # pseudo
    # checkifgpslock()
    gpsdata = recordgps()
    cached_data_obj = gpsdata
    log(gpsdata)
    send("ANTENNAPOWER OFF")
    return gpsdata
    # end pseudo


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
        line = ser.readline()  # Read in a full message from serial

        parse_gps_packet(line)  # Dispatch command
        # logger.info(line)
        # print(rr)
        # log('GOT: '+rr)


def findnth(msg, val, n):
    parts = msg.split(val, n + 1)
    if len(parts) <= n + 1:
        return -1
    return len(msg) - len(parts[-1]) - len(val)


def parse_xyz_packet(packet):
    logger.info("parsing xyz")
    packet = packet[findnth(packet, ' ', 7) + 1:]

    result = {}
    # specific message @ https://docs.novatel.com/OEM7/Content/PDFs/OEM7_Commands_Logs_Manual.pdf
    # pg.434 table.73
    status_code = {'SOL_COMPUTED': 0, 'INSUFFICIENT_OBS': -1, 'NO_CONVERGENCE': 2,
                   'SINGULARITY': 3, 'COV_TRACE': 4, 'TEST_DIST': 5,
                   'COLD_START': 6, 'V_H_LIMIT': 7, 'VARIANCE': 8,
                   'RESIDUALS': 9, 'INTEGRITY_WARNING': 13, 'PENDING': 18,
                   'INVALID_FIX': 19, 'UNAUTHORIZED': 20, 'INVALID_RATE': 22
                   }
    result['status'] = status_code[packet[:findnth(packet, ' ', 0)]]
    result['x_vel'] = float(packet[findnth(packet, ' ', 1) + 1:findnth(packet, ' ', 2)])
    result['y_vel'] = float(packet[findnth(packet, ' ', 2) + 1:findnth(packet, ' ', 3)])
    result['z_vel'] = float(packet[findnth(packet, ' ', 3) + 1:findnth(packet, ' ', 4)])

    return result


def parse_nmea_obj(packet):
    logger.debug("parsing nmea")
    if (packet is None):
        return
    else:
        return {'lat': packet.lat, 'lon': packet.lon, 'alt': packet.altitude, 'alt_unit': packet.altitude_units,
                'lon_dir': packet.lon_dir, 'lat_dir': packet.lat_dir, 'time': packet.timestamp}


def parse_gps_packet(packet):
    global cached_nmea_obj, cached_xyz_obj, cached_data_obj
    packet = str(packet)[2:-5]
    logger.debug(packet)
    logger.debug(packet[0:6])
    if packet[0:6] == '$GPGGA':
        logger.info('POS UPDATE')
        try:
            nmea_obj = pynmea2.parse(packet)
        except:
            logger.error("PARSING ERROR")
            nmea_obj = None
        cached_nmea_obj = parse_nmea_obj(nmea_obj)
        update_time(cached_nmea_obj['time'])
    elif packet[0:8] == '<BESTXYZ':
        logger.info("VEL UPDATE")
        packet = ser.readline()
        xyz_obj = parse_xyz_packet(packet[6:-33].decode("ascii"))
        cached_xyz_obj = xyz_obj
        cached_data_obj = merge(cached_nmea_obj, cached_xyz_obj)
    logger.debug("data: " + str(get_data()))


def get_data():
    global cached_nmea_obj, cached_xyz_obj, cached_data_obj
    return cached_data_obj


def merge(x, y):
    logger.debug("merging")
    if (x is not None and y is not None):
        z = x.copy()
        z.update(y)
        return z


def gpsbeacon():
    global cached_nmea_obj, cached_xyz_obj
    while True:
        time.sleep(gpsperiod)
        if cached_nmea_obj is not None:
            aprs.enqueue(
                str(cached_nmea_obj.altitude) + str(cached_nmea_obj.altitude_units) + str(cached_nmea_obj.lat) + str(
                    cached_nmea_obj.lat_dir) + str(cached_nmea_obj.lon) + str(cached_nmea_obj.lon_dir))


def update_time(time):
    """
    Update system time based on the given time.
    :param time: A `time` object in UTC format.
    """
    os.system('date -s "' + str(time.hour) + ':' + str(time.minute) + ':' + str(time.second) + ' UTC"')


def keyin():
    while True:
        in1 = input("Type Command: ")  # Use `raw_input()` if working with Python2
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


def on_startup():
    global gpsperiod, t1, ser, logfile, tlt, cached_nmea_obj, cached_xyz_obj, t3
    # cached_nmea_obj = (None,None)
    cached_nmea_obj = None
    cached_xyz_obj = None
    gpsperiod = 10

    # Opens the serial port for all methods to use with 19200 baud
    # if config['gps']['simulate']:
    #     s_name = os.ttyname(ser_slave)
    #     ser = serial.Serial(s_name, 19200)
    #     logger.info("Serial started on " + ser.name)
    # else:
    #     ser = serial.Serial(config['gps']['serial_port'], 19200)

    # REPLACE WITH /dev/ttyUSBx if 1 DOESNT WORK
    # serialPort = "/dev/ttyS3"

    t1 = ThreadHandler(target=partial(listen), name="gps-listen", parent_logger=logger)
    t3 = ThreadHandler(target=partial(gpsbeacon), name="gps-gpsbeacon", parent_logger=logger)

    eps.pin_on("gps")
    tlt = time.localtime()

    # Open the log file
    log_dir = os.path.join(config['core']['log_dir'], 'gps')
    filename = 'gps' + '-'.join([str(x) for x in time.localtime()[0:3]])
    # ensure that the GPS log directory exists
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    logfile = open(os.path.join(log_dir, filename + '.txt'), 'a+')

    log('RUN@' + '-'.join([str(x) for x in tlt[3:5]]))

    start_loop()
    # enter_normal_mode()


def wait_for_signal():
    a = True
    logger.info("WAITING FOR GPS SIGNAL")
    send("log gpgga ontime 1")
    while a:
        try:
            packet = ser.readline()[1:-5].decode("ascii")
            packet = pynmea2.parse(packet)
            if (packet.lon != ''):
                logger.info("GPS SIGNAL ACQUIRED")
                send("unlogall")
                return
            else:
                continue
        except:
            continue
    return


def start_loop():
    global t1, t2
    send('ECHO OFF')
    send('UNLOGALL')
    send('ANTENNAPOWER ON')
    send('ASSIGNALL AUTO')
    send('FIX AUTO')
    wait_for_signal()
    send('log gpgga ontime 5')
    send('log bestxyz ontime 5')
    t1.start()
    # t3.start()


# TODO: Need to know what needs to be done in normal, low power, and emergency modes.
def enter_normal_mode():
    # UPDATE GPS MODULE INTERNAL COORDINATES EVERY 10 MINUTES
    # update_internal_coords() IF THIS METHOD IS NECESSARY MESSAGE ME(Anup)
    # time.sleep(600)
    eps.pin_on("gps")
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


def log(msg):
    """
    Write a message to the logfile. Use this function to log messages.
    :param msg: Message to write to the logfile.
    """
    global logfile
    logfile.write(msg + '\n')
    logfile.flush()


if __name__ == '__main__':
    t2 = ThreadHandler(target=partial(keyin), name="gps-keyin", parent_logger=logger)
    t2.start()

    while True:
        time.sleep(1)
