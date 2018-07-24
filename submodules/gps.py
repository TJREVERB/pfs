import serial
import time
import sys
import logging

from threading import Thread
from core import config

#EDIT THIS TO WORK WITH GPS

def on_startup():
    global bperiod, t1, ser
    bperiod = 60
    serialPort = config['aprs']['serial_port']
    ser = serial.Serial(serialPort, 19200)
    t1 = Thread(target=listen, args=())
    t1.daemon = True
    t1.start()

def enter_normal_mode():
    global bperiod
    bperiod = 60


def enter_low_power_mode():
    global bperiod
    bperiod = 120

def enter_emergency_mode():
    pass


if __name__ == '__main__':
    startup()
    serialPort = sys.argv[1]
    ser = serial.Serial(serialPort, 19200)
    t2 = Thread(target=keyin, args=())
    t2.daemon = True
    t2.start()
    while True:
        time.sleep(1)
