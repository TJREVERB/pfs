import logging
import time
import smbus
from smbus2 import SMBusWrapper

from helpers.threadhandler import ThreadHandler
from functools import partial

# Initialize global variables
logger = logging.getLogger("EPS")
address = 43
epsdict = {'gps': 1, 'magnetorquer': 2, 'aprs': 4, 'iridium': 3, 'antenna': 5, 'a': 6, 'b': 7, 'e': 8, 'd': 9, 'e': 10}


def get_PDM_status(device_name):
    with SMBusWrapper(1) as bus:
        PDM_val = [epsdict[device_name]]
        bus.write_i2c_block_data(address, 0x0E, PDM_val)
        return bus.read_byte(address)  # RETURNS A BYTE, NOT A BIT. OK?

def isModuleOn(device_name):
    with SMBusWrapper(1) as bus:
        PDM_val = [epsdict[device_name]]
        if(get_PDM_status(device_name).equals(0)):
            return False
        else:
            return True

print(isModuleOn('gps'))
