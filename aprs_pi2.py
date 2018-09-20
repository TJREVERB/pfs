import logging
import sys
import time
from threading import Thread

import serial

# import submodules.command_ingest as ci
# from submodules.command_ingest import piprint
# import command_ingest as ci
# from submodules import command_ingest as ci

# from core import config
user = False
if len(sys.argv) > 1:
    if sys.argv[1] == 'user':
        user = True


# open port
def send(msg):
    msg = msg + "\r\n"
    # logging.debug("Hidylan")
    # print(msg)
    # print(bytes(msg,encoding="utf-8"))
    # ser.write(bytes(msg,encoding="utf-8"))
    ser.write(msg.encode("utf-8"))


def listen():
    while (True):
        f = open("aprs_log.txt", "w")
        zz = ser.inWaiting()
        rr = ser.read(size=zz)
        if zz > 0:
            time.sleep(.5)
            try:
                zz = ser.inWaiting()
                print(zz)
                rr += ser.read(size=zz)
                f.write("DOWNLINK: " + rr)
            except serial.SeriaException as e:
                print("It Failed")
            # return (rr)
            # return rr


def keyin():
    counter = 1
    while (True):
        print("sending...")
        in1 = "Ba_this_is_a_test_of_the_CubeSat_comms_system"
        in1 = in1 + str(time.time())
        logging.debug("BYTE COUNT: " + str(len(in1)))
        f = open("aprs_log.txt", "w")
        f.write("UPLINK No. " + str(counter) + " : " + in1)
        if (user):
            send("TJ" + in1 + chr(sum([ord(x) for x in "TJ" + in1]) % 128))
        else:
            send(in1)
        time.sleep(20)
        f.close()
        counter = counter + 1


def beacon():
    while (True):
        time.sleep(bperiod)
        btext = "HELLO WORLD I AM FROMETH TJ"
        send(btext)


def on_startup():
    global bperiod, t1, ser
    bperiod = 60
    # serialPort = config['aprs']['serial_port']
    serialPort = "/dev/ttyUSB0"
    ser = serial.Serial(serialPort, 19200)
    t1 = Thread(target=listen, args=())
    t1.daemon = True
    t1.start()
    # logging.debug("Test")


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
    # serialPort = sys.argv[1]
    # ser = serial.Serial(serialPort, 19200)
    t2 = Thread(target=keyin, args=())
    t2.daemon = True
    t2.start()
    while True:
        time.sleep(1)
