import serial
import time
import sys
import logging

#import submodules.command_ingest as ci
import command_ingest as ci

from threading import Thread
#from core import config
user = False
if len(sys.argv) > 1:
    if sys.argv[1] == 'user':
        user = True

#open port
def send(msg):
    msg = msg + "\r\n"
    #logging.debug("Hidylan")
    #print(msg)
    #print(bytes(msg,encoding="utf-8"))
    #ser.write(bytes(msg,encoding="utf-8"))
    ser.write(msg.encode("utf-8"))
def listen():
    while(True):
        zz = ser.inWaiting()
        rr = ser.read(size = zz)
        if zz > 0:
            time.sleep(.5)
            zz = ser.inWaiting()
            rr += ser.read(size = zz)
            ci.piprint(rr)
            #return (rr)
            #return rr


def keyin():
    while(True):
        in1 = raw_input("Type command: ")
        if(user):
            sum = sum([int(x) for x in "TJ"+in1])
            send("TJ"+in1+str(sum%256))
        else:
            send(in1)

def beacon():
    while(True):
        time.sleep(bperiod)
        btext = "HELLO WORLD I AM FROMETH TJ"
        send(btext)


def on_startup():
    global bperiod, t1, ser
    bperiod = 60
    #serialPort = config['aprs']['serial_port']
    serialPort = "/dev/ttyUSB0"
    ser = serial.Serial(serialPort, 19200)
    t1 = Thread(target=listen, args=())
    t1.daemon = True
    t1.start()
    #logging.debug("Test")
def enter_normal_mode():
    global bperiod
    bperiod = 60


def enter_low_power_mode():
    global bperiod
    bperiod = 120

def enter_emergency_mode():
    pass


if __name__ == '__main__':
    on_startup()
    #serialPort = sys.argv[1]
    #ser = serial.Serial(serialPort, 19200)
    t2 = Thread(target=keyin, args=())
    t2.daemon = True
    t2.start()
    while True:
        time.sleep(1)
