import serial
import time
import sys

from . import aprs
from . import gps

from threading import Thread
from core import config
from subprocess import call
import logging


#EDIT THIS TO WORK WITH GPS
def sendgpsthruaprs(givenarg):
    global fakegps
    fakegps = 12347337
    aprs.send(str(fakegps)+'---'+str(givenarg))
def querygps():
    global cachedgps

    return cachedgps
def querypastgps(index):
    #RETURN A PAST GPS COORDINATE BY INDEX
    #REFERENCE OWN GPS LOGS
    return
def passivegps():
    #PASSIVELY UPDATE cachedgps According to gps period
    global cachedgps, gpsperiod
    while True:
        time.sleep(gpsperiod)
        cachedgps = getsinglegps()

def getsinglegps():
    #EXAMPLE METHOD THAT STILL NEEDS TO BE FLESHED OUT
    #AS YOU CAN SEE THERRE'S STILL A TON TO DO
    send("ANTENNAPOWER ON")
    #pseudo
    #checkifgpslock()
    gpsdata = recordgps()
    log(gpsdata)
    send("ANTENNAPOWER OFF")
    return gpsdata
    #end pseudo
def parsegps(bytes):
    str(bytes)
def send(msg):
    msg += "\n"
    ser.write(msg.encode("utf-8"))
def listen():
    while(True):
        zz = ser.inWaiting()
        rr = ser.read(size = zz)
        if zz > 0:
            time.sleep(.5)
            zz = ser.inWaiting()
            rr += ser.read(size = zz)
            logging.info('FROM GPS: '+str(rr))
            #print(rr)
            #log('GOT: '+rr)
def keyin():
    while(True):
        #GET INPUT FROM YOUR OWN TERMINAL
        #TRY input("shihaoiscoolforcommentingstuff") IF raw_input() doesn't work
        in1 = input("Type Command: ")
        send(in1)
        #send("TJ" + in1 + chr(sum([ord(x) for x in "TJ" + in1]) % 128))
def on_startup():
    #GLOBAL VARIABLES ARE NEEDED IF YOU "CREATE" VARIABLES WITHIN THIS METHOD
    #AND ACCESS THEM ELSEWHERE
    global gpsperiod, t1, ser, logfile, tlt, cachedgps
    #cachedgps = (None,None)
    cachedgps = None
    gpsperiod = 60
    serialPort = config['gps']['serial_port']
    #REPLACE WITH COMx IF ON WINDOWS
    #REPLACE WITH /dev/ttyUSBx if 1 DOESNT WORK
    #serialPort = "/dev/ttyS3"
    #OPENS THE SERIAL PORT FOR ALL METHODS TO USE WITH 19200 BAUD
    ser = serial.Serial(serialPort, 9600)
    #CREATES A THREAD THAT RUNS THE LISTEN METHOD
    t1 = Thread(target=listen, args=())
    t1.daemon = True
    t1.start()
    tlt = time.localtime()
    filename = 'gps'+'-'.join([str(x) for x in tlt[0:3]])
    logfile = open('/root/TJREVERB/pFS/submodules/logs/gps/'+filename+'.txt','a+')
    log('RUN@'+'-'.join([str(x) for x in tlt[3:5]]))

    send("ANTENNAPOWER OFF")
# I NEED TO KNOW WHAT NEEDS TO BE DONE IN NORMAL, LOW POWER, AND EMERGENCY MODES
def enter_normal_mode():
    #UPDATE GPS MODULE INTERNAL COORDINATES EVERY 10 MINUTES
    update_internal_coords()
    time.sleep(600)


def enter_low_power_mode():
    #UPDATE GPS MODULE INTERNAL COORDINATES EVERY HOUR
    update_internal_coords()
    time.sleep(3600)

def enter_emergency_mode():
    #ALL GPS FUNCTIONS OFF. LOWEST POWER POSSIBLE
    call("unlog") #I don't know any other off functions - comment some here or message me (Rishabh) some on slack

#USE THIS LOG FUNCTION
def log(msg):
    global logfile
    logfile.write(msg+'\n')
    logfile.flush()

if __name__ == '__main__':

    t2 = Thread(target=keyin, args=())
    t2.daemon = True
    t2.start()
    while True:
        time.sleep(1)
