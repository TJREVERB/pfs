import time
from threading import Thread

import smbus

bus = smbus.SMBus(1)
address = 0x68


def acc():
    global ax, ay, az, datasave
    ax = bus.read_byte_data(address, 0x3B)
    ay = bus.read_byte_data(address, 0x3D)
    az = bus.read_byte_data(address, 0x3F)
    # print("acc", ax, ay, az)


def gyr():
    global gx, gy, gz, datasave
    gx = bus.read_byte_data(address, 0x43)
    gy = bus.read_byte_data(address, 0x45)
    gz = bus.read_byte_data(address, 0x47)
    # print("gyr", gx, gy, gz)


def acc_gyr():
    global speriod, datasave
    while True:
        acc()
        gyr()
        templist = [str(x) for x in [ax, ay, az, gx, gy, gz]]
        datapoint = ':'.join(templist)
        print(datapoint)
        datasave += [datapoint]
        time.sleep(speriod)


def on_startup():
    global speriod, datasave
    enter_normal_mode()
    datasave = []
    t1 = Thread(target=acc_gyr, args=())
    t1.daemon = True
    t1.start()


def enter_normal_mode():
    global speriod
    speriod = 1


def enter_low_power_mode():
    global speriod
    speriod = 20


def enter_emergency_mode():
    global speriod
    speriod = 60


if __name__ == '__main__':
    on_startup()
    while True:
        time.sleep(1)
