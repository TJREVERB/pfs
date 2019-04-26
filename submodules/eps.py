import logging
import time
from functools import partial

import smbus
from smbus2 import SMBusWrapper

from core.mode import Mode
from helpers.threadhandler import ThreadHandler

# Initialize global variables
logger = logging.getLogger("EPS")
address = 43
epsdict = {'gps': 1, 'magnetorquer': 2, 'aprs': 4, 'iridium': 3,
           'antenna': 5, 'a': 6, 'b': 7, 'c': 8, 'd': 9, 'e': 10}
mode = Mode.NORMAL


def pin_on(device_name) -> bool:
    if state != Mode.NORMAL:
        return False
    with SMBusWrapper(1) as bus:
        PDM_val = [epsdict[device_name]]

        if get_PDM_status(device_name) == 1:
            logger.error("Pin is already ON.")
            return True
        else:
            bus.write_i2c_block_data(address, 0x12, PDM_val)

            if get_PDM_status(device_name) == 1:  # PDM is ON
                logger.debug("Pin communication successful. \
                Pin is now ON.")
                return True
            else:
                logger.error("Pin communication unsuccessful")
                return False


def reboot_device(device_name, sleeptime) -> None:
    pin_off(device_name)
    time.sleep(sleeptime)
    pin_on(device_name)
    time.sleep(sleeptime)


def pin_off(device_name) -> bool:
    with SMBusWrapper(1) as bus:
        PDM_val = [epsdict[device_name]]

        if get_PDM_status(device_name) == 0:
            logger.error("Pin is already OFF.")
            return True
        else:
            bus.write_i2c_block_data(address, 0x13, PDM_val)

            if get_PDM_status(device_name) == 0:  # PDM is OFF
                logger.debug("Pin communication successful. \
                  Pin is now OFF.")
            else:
                logger.error("Pin communication unsuccessful")
                return False


def get_PDM_status(device_name):
    with SMBusWrapper(1) as bus:
        PDM_val = [epsdict[device_name]]
        bus.write_i2c_block_data(address, 0x0E, PDM_val)
        return bus.read_byte(address)  # RETURNS A BYTE, NOT A BIT. OK?


def is_module_on(device_name) -> bool:
    with SMBusWrapper(1) as bus:
        PDM_val = [epsdict[device_name]]
        if get_PDM_status(device_name).equals(0):
            return False
        else:
            return True


def get_board_status():
    with SMBusWrapper(1) as bus:
        return bus.read_i2c_block_data(address, 0x01)


def set_system_watchdog_timeout(timeout):
    with SMBusWrapper(1) as bus:
        timeout = [timeout]
        bus.write_i2c_block_data(address, 0x06, timeout)


def get_bcr1_volts():
    with SMBusWrapper(1) as bus:
        bus.write_i2c_block_data(address, 0x10, 0x00)
        return bus.read_byte(address)


def get_bcr1_amps_a():
    with SMBusWrapper(1) as bus:
        bus.write_i2c_block_data(address, 0x10, 0x01)
        return bus.read_byte(address)


def get_bcr1_amps_b():
    with SMBusWrapper(1) as bus:
        bus.write_i2c_block_data(address, 0x10, 0x02)
        return bus.read_byte(address)


def get_battery_bus_volts():  # TODO: Verify
    with SMBusWrapper(1) as bus:
        bus.write_i2c_block_data(address, 0x10, 0x23)
        return bus.read_byte(address)


def get_board_telem(data):
    with SMBusWrapper(1) as bus:
        bus.write_byte_data(address, 0x10, 0x23)
        return bus.read_byte(address)


def led_on_off() -> None:
    looptime = 20  # FIXME: Was 30
    while True:
        pin_on('aprs')
        time.sleep(looptime)
        pin_off('aprs')
        time.sleep(looptime)


def board_check() -> None:
    while True:
        logger.debug(get_board_telem(0x23))
        time.sleep(7)


def start():
    global address, bus, state

    bus = smbus.SMBus(1)
    state = 'NORMAL'
    # for key,val in epsdict.items():
    #    if val > 0:
    #        pin_off(key)
    #        time.sleep(1)
    # Create all the background threads
    t1 = ThreadHandler(target=partial(led_on_off),
                       name="eps-led_on_off", parent_logger=logger)
    t2 = ThreadHandler(target=partial(board_check),
                       name="eps-board_check", parent_logger=logger)

    # Start the background threads
    # t1.start()
    t2.start()

    # TESTING PURPOSES ONLY
    # test the LEDs - turn them all on
    # for key in epsdict.keys():
    #   pin_on(key)


# TODO: Update these methods. Currently only holds placeholder methods.
def enter_normal_mode():
    global state
    state = Mode.NORMAL


def enter_low_power_mode():
    global state
    state = Mode.LOW_POWER


def enter_emergency_mode():
    global state
    state = Mode.EMERGENCY
