import os
import serial
import threading

from core.threadhandler import ThreadHandler


def start(master, slave):
    global ser, ser_master, ser_slave, t1, t2
    ser_master = master
    ser_slave = slave

    ser = serial.Serial(os.ttyname(ser_master), 19200)

    t1 = ThreadHandler(name="receive", target=receive_listener)
    t2 = ThreadHandler(name="transmit", target=transmit_listener)


def receive_listener():
    while True:
        print(os.read(ser_master), 1000)


def transmit_listener():
    line = b''
    while not line.endswith(b'\n'):
        res = os.read(ser_master, 1000)
        line += res
    ser.write(line)

