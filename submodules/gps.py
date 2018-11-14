import logging
import os
import sys
import time
from subprocess import call
from threading import Thread

import pynmea2
import serial

from core import config
from . import aprs
from . import adcs

logger = logging.getLogger("GPS")

lat = -1.0
lon = -1.0
alt = -1.0



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
        # Read in a full message from serial
        line = ser.readline()
        # Dispatch command
        parse_gps_packet(line)
        # logger.info(line)
        # print(rr)
        # log('GOT: '+rr)

def findnth(msg, val, n):
    parts= msg.split(val, n+1)
    if len(parts)<=n+1:
        return -1
    return len(msg)-len(parts[-1])-len(val)


def parse_xyz_packet(packet):
    packet = packet[findnth(packet,' ',7)+1:]

    result = {}
    #specific message @ https://docs.novatel.com/OEM7/Content/PDFs/OEM7_Commands_Logs_Manual.pdf
    #pg.434 table.73
    status_code = {'SOL_COMPUTED':0,'INSUFFICIENT_OBS':-1,'NO_CONVERGENCE':2,
                   'SINGULARITY':3,'COV_TRACE':4,'TEST_DIST':5,
                   'COLD_START':6,'V_H_LIMIT':7,'VARIANCE':8,
                   'RESIDUALS':9,'INTEGRITY_WARNING':13,'PENDING':18,
                   'INVALID_FIX':19,'UNAUTHORIZED':20,'INVALID_RATE':22
                   }
    result['latency'] = float(packet[-5:])
    result['status'] = status_code[packet[:findnth(packet,' ',0)]]
    result['x_vel'] = float(packet[findnth(packet,' ',1)+1:findnth(packet,' ',2)])
    result['y_vel'] = float(packet[findnth(packet,' ',2)+1:findnth(packet,' ',3)])
    result['z_vel'] = float(packet[findnth(packet,' ',3)+1:findnth(packet,' ',4)])

    return result

def parse_nmea_obj(packet):
    result = {}
    result['lat'] = packet.lat
    result['lon'] = packet.lon
    result['alt'] = packet.alt
    result['time'] = packet.timestamp
    return result    

def parse_gps_packet(packet):
    global cached_nmea_obj, lat, lon, alt, cached_xyz_obj, ser
    packet = str(packet)[2:-5]
    logger.info(packet)
    # packet = packet[]
    logger.debug(packet[0:6])
    if packet[0:6] == '$GPGGA':
        # logger.info('POS UPDATE')
        nmea_obj = pynmea2.parse(packet)
        cached_nmea_obj = parse_nmea_obj(nmea_obj)
        lon = cached_nmea_obj['lon']
        lat = cached_nmea_obj['lat']
        alt = cached_nmea_obj['alt']
        updateTime(cached_nmea_obj['time'])
    elif packet[0:8] == '<BESTXYZ':
        packet = ser.readline()
        xyz_obj = parse_xyz_packet(packet[6:-33].decode("ascii"))
        cached_xyz_obj = xyz_obj
    cached_data_obj = merge(cached_nmea_obj,cached_xyz_obj)
        


def merge(x,y):
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
        if cached_xyz_obj is not None:
           adcs.updateVals(cached_xyz_obj)


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
    # GLOBAL VARIABLES ARE NEEDED IF YOU "CREATE" VARIABLES WITHIN THIS METHOD
    # AND ACCESS THEM ELSEWHERE
    global gpsperiod, t1, ser, logfile, tlt, cached_nmea_obj, cached_xyz_obj
    # cached_nmea_obj = (None,None)
    cached_nmea_obj = None
    cached_xyz_obj = None
    gpsperiod = 10
    serialPort = config['gps']['serial_port']
    # REPLACE WITH COMx IF ON WINDOWS
    # REPLACE WITH /dev/ttyUSBx if 1 DOESNT WORK
    # serialPort = "/dev/ttyS3"
    # OPENS THE SERIAL PORT FOR ALL METHODS TO USE WITH 19200 BAUD
    ser = serial.Serial(serialPort, 9600)
    # CREATES A THREAD THAT RUNS THE LISTEN METHOD
    t1 = Thread(target=listen, args=(), daemon=True)
    t1.start()

    t3 = Thread(target=gpsbeacon, args=(), daemon=True)
    t3.start()

    tlt = time.localtime()

    # Open the log file
    log_dir = os.path.join(config['core']['log_dir'], 'gps')
    filename = 'gps' + '-'.join([str(x) for x in time.localtime()[0:3]])
    # ensure that the GPS log directory exists
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    logfile = open(os.path.join(log_dir, filename + '.txt'), 'a+')

    log('RUN@' + '-'.join([str(x) for x in tlt[3:5]]))

    send('ECHO OFF')
    send('UNLOGALL')
    send('ANTENNAPOWER ON')
    send('FIX AUTO')
    send('log gpgga ontime 8')
    # Check for signal, pynmea.parse throws pynmea2.nema.ChecksumError if there is no signal
    while(True):
        try:
            pynmea2.parse(ser.readline()[2:-5])
            break
        except pynmea2.nmea.ChecksumError:
            time.sleep(1)

    send('log bestxyz ontime 9')
    # enter_normal_mode()


# I NEED TO KNOW WHAT NEEDS TO BE DONE IN NORMAL, LOW POWER, AND EMERGENCY MODES
def enter_normal_mode():
    # UPDATE GPS MODULE INTERNAL COORDINATES EVERY 10 MINUTES
    # update_internal_coords() IF THIS METHOD IS NECESSARY MESSAGE ME(Anup)
    # time.sleep(600)
    send('ECHO OFF')
    send('FIX AUTO')
    send('ASSIGNALL AUTO')
    send('ANTENNAPOWER ON')
    send('log gpgga ontime 600') #update lat/lon/alt
    send('log bestxyz ontime 600') #update x-y-z vel


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
