import serial
import time
import sys

import command_injest

from threading import Thread

#open port
def send(msg):
    msg += "\n"
    ser.write(bytes(msg,encoding="utf-8"))
def listen():
    while(True):
        zz = ser.inWaiting()
        rr = b''
        if zz > 0:
            time.sleep(.5)
            rr += ser.read(size = zz)
            command_injest.dispatch_command(rr)
            #return (rr)
            #return rr
def keyin():
    while(True):
        in1 = input("Type command: ")
        send(in1)
def beacon():
    while(True):
        time.sleep(bperiod)
        btext = "HELLO WORLD I AM FROMETH TJ"
        send(btext)
def startup():
    global bperiod, t1, ser
    bperiod = 60
    serialPort = "/dev/ttyUSB0"
    ser = serial.Serial(serialPort, 19200)
    t1 = Thread(target=listen, args=())
    t1.daemon = True
    t1.start()
def lowerpower():
    bperiod = 120
if __name__ == '__main__':
    startup()
    serialPort = sys.argv[1]
    ser = serial.Serial(serialPort, 19200)
    t2 = Thread(target=keyin, args=())
    t2.daemon = True
    t2.start()
    while True:
        time.sleep(1)
