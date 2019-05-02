import logging
import time

import smbus

from submodules import telemetry
from submodules import aprs

from core.mode import Mode
from core.threadhandler import ThreadHandler
from functools import partial

bus = smbus.SMBus(1)
address = 0x68  # TODO: Double check here: http://www.invensense.com/wp-content/uploads/2017/11/RM-MPU-9250A-00-v1.6.pdf


def get_current_data():
    global current_data
    return current_data


def imu_beacon():
    global current_data
    while state == Mode.NORMAL:
        if current_data is not None:
            aprs.send(current_data)
            logging.debug('IMU DATASAVE CLEAR')


def acc():  # TODO: NEED TO CONVERT BYTE DATA FOR ADCS
    global ax, ay, az
    ax = bus.read_byte_data(address, 0x3B)
    ay = bus.read_byte_data(address, 0x3D)
    az = bus.read_byte_data(address, 0x3F)
    return ax, ay, az


def gyr():  # TODO: NEED TO CONVERT BYTE DATA FOR ADCS
    global gx, gy, gz
    gx = bus.read_byte_data(address, 0x43)
    gy = bus.read_byte_data(address, 0x45)
    gz = bus.read_byte_data(address, 0x47)
    return gx, gy, gz


def acc_gyr():
    global current_data
    while state == Mode.NORMAL:
        try:
            acc()
        except:
            logging.error("ACC FAILED")
            telemetry.enqueue_event_message("I01")
        try:
            gyr()
        except:
            logging.error("GYR FAILED")
            telemetry.enqueue_event_message("I02")
        current_data = ':'.join([str(x) for x in [ax, ay, az, gx, gy, gz]])
        logging.debug('IMU ADD DATA POINT')


def start():
    global current_data, state

    state = None
    current_data = None

    t1 = ThreadHandler(target=partial(acc_gyr), name="imu-acc_gyr")
    t1.start()

    t2 = ThreadHandler(target=partial(imu_beacon), name="imu-imu_beacon")
    t2.start()


def enter_normal_mode():
    global state
    state = Mode.NORMAL


def enter_low_power_mode():
    global state
    state = Mode.LOW_POWER


def enter_emergency_mode():
    global state
    state = Mode.EMERGENCY


if __name__ == '__main__':
    start()

    while True:
        time.sleep(1)
