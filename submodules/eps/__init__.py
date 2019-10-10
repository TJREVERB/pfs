import logging
import time
import smbus
import yaml

from smbus2 import SMBusWrapper
from functools import partial

from core.mode import Mode
from core.threadhandler import ThreadHandler
from core.error import Error
from core.log import Log
from submodules import telemetry


def pin_on(device_name) -> bool:
    with SMBusWrapper(1) as bus:
        if device_name in epsdict:
            PDM_val = epsdict[device_name]
        else:
            message = "Device name \'{}\' INVALID. Aborting command.".format(device_name)
            logger.error(message)
            log = Error(sys_name="EPS", msg=message)
            telemetry.enqueue(log)
            return False

        if get_PDM_status(device_name) == 1:
            message = "Pin {} ({}) is already ON.".format(epsdict[device_name], device_name)
            logger.debug(message)  # Log to console for debugging
            log = Log(sys_name="EPS", lvl="INFO", msg=message)  # Create log instance
            telemetry.enqueue(log)  # Push to telemetry stack
            return True
        else:
            bus.write_byte_data(address, 0x12, PDM_val)  # Attempt to execute pin on

            if get_PDM_status(device_name) == 1:  # PDM is ON
                message = "Pin {} ({}) communication successful. Pin is now ON.".format(
                    epsdict[device_name], device_name)
                logger.debug(message)
                log = Log(sys_name="EPS", lvl="INFO", msg=message)
                telemetry.enqueue(log)
                return True
            else:  # Something is big broken
                message = "Pin {} ({}) communication NOT successful. Pin is still OFF.".format(
                    epsdict[device_name], device_name)
                logger.error(message)
                log = Error(sys_name="EPS", msg=message)
                telemetry.enqueue(log)
                return False


def reboot_device(device_name, wait_time_after_off, wait_time_after_on) -> bool:
    """
    :param wait_time_after_off: Time to wait after turning the device off
    :param wait_time_after_on: Time to wait before verifying the reboot was successful 
        (i.e. after turn on command)
    :return: Boolean representing whether or not the reboot was successful
    """
    if not pin_off(device_name):
        return False
    message = "From Pin {} ({}) reboot: sleeping {} second(s) after turn off.".format(
        epsdict[device_name], device_name, wait_time_after_off)
    logger.debug(message)
    log = Log(sys_name="EPS", lvl="INFO", msg=message)
    telemetry.enqueue(message)
    time.sleep(wait_time_after_off)  # Wait for specified time

    if not pin_on(device_name):
        return False
    message = "From Pin {} ({}) reboot: sleeping {} second(s) after turn on.".format(
        epsdict[device_name], device_name, wait_time_after_off)
    logger.debug(message)
    log = Log(sys_name="EPS", lvl="INFO", msg=message)
    telemetry.enqueue(message)
    time.sleep(wait_time_after_on)

    if get_PDM_status(device_name) == 1:
        message = "Pin {} ({}) reboot successful.".format(epsdict[device_name], device_name)
        logger.debug(message)
        log = Log(sys_name="EPS", lvl="INFO", msg=message)
        telemetry.enqueue(message)
        return True
    else:
        message = "Pin {} ({}) reboot NOT successful. Recommend PDM status check in {} second(s).".format(
            epsdict[device_name], device_name, wait_time_after_on)
        logger.error(message)
        log = Error(sys_name="EPS", msg=message)
        telemetry.enqueue(message)
        return False


def pin_off(device_name) -> bool:
    with SMBusWrapper(1) as bus:
        if device_name in epsdict:
            PDM_val = epsdict[device_name]
        else:
            message = "Device name \'{}\' INVALID. Aborting command.".format(device_name)
            logger.error(message)
            log = Error(sys_name="EPS", msg=message)
            telemetry.enqueue(log)
            return False

        if get_PDM_status(device_name) == 0:
            message = "Pin {} ({}) is already OFF.".format(epsdict[device_name], device_name)
            logger.debug(message)  # Log to console for debugging
            log = Log(sys_name="EPS", lvl="INFO", msg=message)  # Create log instance
            telemetry.enqueue(log)  # Push to telemetry stack
            return True
        else:
            bus.write_byte_data(address, 0x13, PDM_val)  # Attempt to execute pin off

            if get_PDM_status(device_name) == 0:  # PDM is OFF
                message = "Pin {} ({}) communication successful. Pin is now OFF.".format(
                    epsdict[device_name], device_name)
                logger.debug(message)
                log = Log(sys_name="EPS", lvl="INFO", msg=message)
                telemetry.enqueue(log)
                return True
            else:
                message = "Pin {} ({}) communication NOT successful. Pin is still ON.".format(
                    epsdict[device_name], device_name)
                logger.error(message)
                log = Error(sys_name="EPS", msg=message)
                telemetry.enqueue(log)
                return False

# TODO: Finish status integrity method
def verify_status_integrity(device_name):
    arr = []
    val = int(get_PDM_status(device_name))
    for x in range(0, 60):
        arr.append(get_PDM_status(device_name))
        logger.debug(str(arr[x]))
        if val != arr[x]:
            logger.debug("No match at index = " + str(x))
        time.sleep(0.25)


def send_pin_statuses() -> bool:
    try:
        statuses = []
        for device in epsdict:
            statuses.append(get_PDM_status(device))
        message = "Enqueuing Pin statuses to telemetry."
        logger.debug(message)
        log = Log(sys_name="EPS", lvl="INFO", msg=message)
        telemetry.enqueue(log)

        log = Log(sys_name="EPS", lvl="DATA", msg=statuses)
        telemetry.enqueue(statuses)
        
        message = "Pin statuses packed and sent to enqueued into telemetry. Next status check: \
            {} second(s).".format(config['eps']['status_check_interval'])
        logger.debug(message)
        log = Log(sys_name="EPS", lvl="INFO", msg=message)
        telemetry.enqueue(log)
        return True
    except:
        message = "Enqueuing Pin statuses to telemetry FAILED. Next status check: {} second(s).".format(
            config['eps']['status_check_interval'])
        logger.error(message)
        log = Error(sys_name="EPS", msg=message)
        telemetry.enqueue(log)
        return False


def get_PDM_status(device_name):
    with SMBusWrapper(1) as bus:
        PDM_val = epsdict[device_name]
        bus.write_byte_data(address, 0x0E, PDM_val)
        return bus.read_byte(address)  # RETURNS A BYTE, NOT A BIT. OK?


def is_module_on(device_name) -> bool:
    with SMBusWrapper(1) as bus:
        PDM_val = epsdict[device_name]
        if get_PDM_status(device_name).equals(0):
            return False
        else:
            return True


def get_board_status():
    with SMBusWrapper(1) as bus:
        return bus.read_byte_data(address, 0x01)


def set_system_watchdog_timeout(timeout):
    with SMBusWrapper(1) as bus:
        timeout = [timeout]
        bus.write_byte_data(address, 0x06, timeout)


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


# FIXME: Invalid return type: should be int list (so add a while loop)
def get_board_telem(data):
    with SMBusWrapper(1) as bus:
        bus.write_byte_data(address, 0x10, 0x23)
        return bus.read_byte(address)


def board_check() -> None:
    while True:
        logger.debug(get_board_telem(0x23))
        time.sleep(7)


def start():
    global address, bus, logger, address, epsdict
    bus = smbus.SMBus(1)
    # Create all the background threads
    t2 = ThreadHandler(target=partial(board_check),
                       name="eps-board_check", parent_logger=logger)
    logger = logging.getLogger("EPS")
    address = 0x57
    epsdict = {'a': 1, 'i2c': 2, 'c': 3, 'antenna': 4,
            'pi': 5, 'iridium': 6, 'aprs': 7, 'h': 8, 'i': 9, 'j': 10}
    with open('config/config_default.yml') as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as error:
            logger.error(error)
