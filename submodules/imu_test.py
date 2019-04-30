import logging
import time

import smbus
import threading

bus = smbus.SMBus(1)
address = 0x68 

def get_current_data():
    global current_data
    current_data = []
    current_data.append(get_acc())
    current_data.append(get_gyr())
    return current_data

def get_acc():
    global ax, ay, az
    try:
        ax = bus.read_byte_data(address, 0x3B)
        ay = bus.read_byte_data(address, 0x3D)
        az = bus.read_byte_data(address, 0x3F)
    except:
        print("Getting accelerometer data failed.")

    return ax, ay, az

def get_gyr():
    global gx, gy, gz
    try:
        gx = bus.read_byte_data(address, 0x43)
        gy = bus.read_byte_data(address, 0x45)
        gz = bus.read_byte_data(address, 0x47)
    except:
        print("Getting gyro data failed.")

    return gx, gy, gz

def start():
    global current_data, state
    state = "NORMAL"
    current_data = None

    start = int(time.time())
    while True:
        while state == "NORMAL":
            now = int(time.time())
            print(get_current_data())
            time.sleep(0.5)
            if (now-start)%10==0:
                print("Entering emergency mode...")
                state = "EMERGENCY"
        time.sleep(3)
        state = "NORMAL"
        print("Entering normal mode...")

if __name__ == "__main__":
    start()
