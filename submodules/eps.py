import logging
import os
import time
import smbus
from smbus2 import SMBusWrapper
from threading import Thread
from typing import Union

import serial

import submodules.command_ingest as ci
from core import config
# Initalize global variables
import submodules.command_ingest
from submodules.command_ingest import logger, dispatch

logger = logging.getLogger("EPS")
pause_sending = False
send_buffer = []
beacon_seen = False
last_telem_time = time.time()
last_message_time = time.time()

user = False
bperiod = 60
ser: Union[serial.Serial, None] = None

address = 43

epsdict = {'gps':0, 'magnetorquer':1, 'aprs':2, \
'iridium':3, 'antenna':4, 'a':5, 'b':6, 'c':7, 'd':8, 'e':9, 'f':10}

def listen():
    while True:
        # Read in a full message from serial
        line = ser.readline()
        # Dispatch command
        parse_aprs_packet(line)
def pin_on(device_name):
    with SMBusWrapper(1) as bus:
        PDM_val = [epsdict[device_name]]
        bus.write_i2c_block_data(address, 0x12, PDM_val)
        if get_PDM_status(device_name) == 1: # PDM is ON
            logger.error("Pin is already ON.")
        else:
            logger.debug("Pin communication successful. \
            Pin is now ON.")
def pin_off(device_name):
    with SMBusWrapper(1) as bus:
        PDM_val = [epsdict[device_name]]
        bus.write_i2c_block_data(address, 0x13, PDM_val)
        if get_PDM_status(device_name) == 0: # PDM is OFF
            logger.error("Pin is already OFF.")
        else:
            logger.debug("Pin communication successful. \
            Pin is now OFF.")
def get_PDM_status(device_name):
    with SMBusWrapper(1) as bus:
        PDM_val = [epsdict[device_name]]
        bus.write_i2c_block_data(address, 0x0E, PDM_val)
        return bus.read_byte(address) #RETURNS A BYTE, NOT A BIT. OK?
def get_board_status():
    with SMBusWrapper(1) as bus:
        return bus.read_i2c_block_data(address, 0x01)
def set_system_watchdog_timeout(timeout):
    with SMBusWrapper(1) as bus:
        timeout = [timeout]
        bus.write_i2c_block_data(address, 0x06, timeout)
def get_BCR1_volts():
    with SMBusWrapper(1) as bus:
        bus.write_i2c_block_data(address, 0x10, 0x00)
        return bus.read_byte(address)
def get_BCR1_amps_A():
    with SMBusWrapper(1) as bus:
        bus.write_i2c_block_data(address, 0x10, 0x01)
        return bus.read_byte(address)
def get_BCR1_amps_B():
    with SMBusWrapper(1) as bus:
        bus.write_i2c_block_data(address, 0x10, 0x02)
        return bus.read_byte(address)
def get_board_telem(data):
    with SMBusWrapper(1) as bus:
        bus.write_i2c_block_data(address, 0x10, 0x23)
        return bus.read_byte(address)
def led_on_off():
    while True:
        pin_on('aprs')
        time.sleep(1)
        pin_off('aprs')
        time.sleep(1)
def board_check():
    while True:
        print(get_board_telem(0x23))
        time.sleep(1)
# Method that is called upon application startup.
def on_startup():
    global ser, logfile
    global address, bus

    bus = smbus.SMBus(1)

    for key,val in epsdict.items():
        if val > 0:
            pin_on(key)
            time.sleep(1)
            pin_off(key)
            time.sleep(1)
    # Create all the background threads
    t1 = Thread(target=led_on_off, args=(), daemon=True)
    t2 = Thread(target=board_check, args=(), daemon=True)
    # Open the log file
    log_dir = os.path.join(config['core']['log_dir'], 'eps')
    filename = 'eps' + '-'.join([str(x) for x in time.localtime()[0:3]])
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    logfile = open(os.path.join(log_dir, filename + '.txt'), 'a+')

    # Mark the start of the log
    log_message('RUN@' + '-'.join([str(x) for x in time.localtime()[3:5]]))

    t1.daemon = True
    # Start the background threads
    t1.start()
    #t1.daemon = True
    t2.daemon = True
    t2.start()
    # Turn on the APRS led
    pin_on('aprs')


# Have the 3 below methods. Say pass if you dont know what to put there yet
# these are in reference to power levels. Shut stuff down if we need to go to
# emergency mode or low power. Entering normal mode should turn them back on
def enter_normal_mode():
    global bperiod
    bperiod = 60


def enter_low_power_mode():
    global bperiod
    bperiod = 120


def enter_emergency_mode():
    pass


def log_message(msg):
    global logfile
    # Write to file
    logfile.write(msg + '\n')
    logfile.flush()
