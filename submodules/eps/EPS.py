import logging
import time
import smbus
import yaml

from functools import partial

from smbus2 import SMBusWrapper
from submodules import telemetry

from helpers.log import Log
from helpers.error import Error
from helpers.threadhandler import ThreadHandler

class EPS():
    def __init__(self, config: dict):
        self.config = config
        self.modules = dict()
        # TODO: Add ThreadHandler object
        self.address = 0x57
        self.eps_dict = {'a':1, 'i2c':2, 'c':3, 'antenna':4, 'pi':5, 'iridium':6, 'aprs':7, 'h':8}

    def pin_on(self, device_name) -> bool:
        with SMBusWrapper(1) as bus:
            if device_name in self.eps_dict:
                PDM_val = self.eps_dict[device_name]
            else:
                message = "Device name \"{}\" INVALID. Aborting command.".format(device_name)
                logger.error(message)
                log = Error(sys_name="EPS", msg=message)
                # telemetry.enqueue(log)
                self.modules["telemetry"].enqueue(log)
                return False

            if get_PDM_status(device_name) == 1:
                message = "Pin {} ({}) is already ON.".format(self.eps_dict[device_name], device_name)
                logger.debug(message)  # Log to console for debugging
                log = Log(sys_name="EPS", lvl="INFO", msg=message)  # Create log instance
                self.modules["telemetry"].enqueue(log)  # Push to telemetry stack
                return True
            else:
                bus.write_byte_data(self.address, 0x12, PDM_val)  # Attempt to execute pin on

                if get_PDM_status(device_name) == 1:  # PDM is ON
                    message = "Pin {} ({}) communication successful. Pin is now ON.".format(
                        self.eps_dict[device_name], device_name)
                    logger.debug(message)
                    log = Log(sys_name="EPS", lvl="INFO", msg=message)
                    self.modules["telemetry"].enqueue(log)
                    return True
                else:  # Something is big broken
                    message = "Pin {} ({}) communication NOT successful. Pin is still OFF.".format(
                        self.eps_dict[device_name], device_name)
                    logger.error(message)
                    log = Error(sys_name="EPS", msg=message)
                    self.modules["telemetry"].enqueue(log)
                    return False

    def pin_off(self, device_name) -> bool:
        with SMBusWrapper(1) as bus:
            if device_name in self.eps_dict:
                PDM_val = self.eps_dict[device_name]
            else:
                message = "Device name \"{}\" INVALID. Aborting command.".format(device_name)
                logger.error(message)
                log = Error(sys_name="EPS", msg=message)
                self.modules["telemetry"].enqueue(log)
                return False

            if get_PDM_status(device_name) == 0:
                message = "Pin {} ({}) is already OFF.".format(self.eps_dict[device_name], device_name)
                logger.debug(message)  # Log to console for debugging
                log = Log(sys_name="EPS", lvl="INFO", msg=message)  # Create log instance
                self.modules["telemetry"].enqueue(log)  # Push to telemetry stack
                return True
            else:
                bus.write_byte_data(self.address, 0x13, PDM_val)  # Attempt to execute pin off

                if get_PDM_status(device_name) == 0:  # PDM is OFF
                    message = "Pin {} ({}) communication successful. Pin is now OFF.".format(
                        self.eps_dict[device_name], device_name)
                    logger.debug(message)
                    log = Log(sys_name="EPS", lvl="INFO", msg=message)
                    self.modules["telemetry"].enqueue(log)
                    return True
                else:
                    message = "Pin {} ({}) communication NOT successful. Pin is still ON.".format(
                        self.eps_dict[device_name], device_name)
                    logger.error(message)
                    log = Error(sys_name="EPS", msg=message)
                    self.modules["telemetry"].enqueue(log)
                    return False

    def reboot_device(self, device_name, wait_after_off=10, wait_after_on=30):
        """
        :param wait_time_after_off: Time to wait after turning the device off
        :param wait_time_after_on: Time to wait before verifying the reboot was successful 
            (i.e. after turn on command)
        :return: Boolean representing whether or not the reboot was successful
        """
        # FIXME: Do we need a self.pin_off() or just pin_off()?
        if not pin_off(device_name):  # If it's still on? Maybe trying to see if pin_off() was successful?
            return False
        # TODO: All code below is unconverted
        message = "From Pin {} ({}) reboot: sleeping {} second(s) after turn off.".format(
            self.epsdict[device_name], device_name, wait_after_off)
        logger.debug(message)
        log = Log(sys_name="EPS", lvl="INFO", msg=message)
        telemetry.enqueue(message)
        time.sleep(wait_after_off)  # Wait for specified time

        if not pin_on(device_name):
            return False
        message = "From Pin {} ({}) reboot: sleeping {} second(s) after turn on.".format(
            self.epsdict[device_name], device_name, wait_after_off)
        logger.debug(message)
        log = Log(sys_name="EPS", lvl="INFO", msg=message)
        telemetry.enqueue(message)
        time.sleep(wait_after_off)

        if get_PDM_status(device_name) == 1:
            message = "Pin {} ({}) reboot successful.".format(self.epsdict[device_name], device_name)
            logger.debug(message)
            log = Log(sys_name="EPS", lvl="INFO", msg=message)
            telemetry.enqueue(message)
            return True
        else:
            message = "Pin {} ({}) reboot NOT successful. Recommend PDM status check in {} second(s).".format(
                self.epsdict[device_name], device_name, wait_after_off)
            logger.error(message)
            log = Error(sys_name="EPS", msg=message)
            telemetry.enqueue(message)
            return False

    def get_PDM_status(self, device_name):
        with SMBusWrapper(1) as bus:
            PDM_val = self.eps_dict[device_name]
            bus.write_byte_data(self.address, 0x0E, PDM_val)
            return bus.read_byte(self.address)

    def is_module_on(self, device_name) -> bool:
        with SMBusWrapper(1) as bus:
            PDM_val = self.eps_dict[device_name]
            if self.get_PDM_status(device_name) == 0:
                return False
            return True

    def get_board_status(self):
        with SMBusWrapper(1) as bus:
            return bus.read_byte_data(self.address, 0x01)

    def get_device_statuses(self) -> dict:
        temp_dict = dict()
        with SMBusWrapper(1) as bus:
            for device_name in self.eps_dict.keys():
                temp_dict.update({device_name, self.get_PDM_status(device_name)})
        return temp_dict

    # TODO: The following are semi-extraneous, need to test
    def get_bcr1_volts(self):
        with SMBusWrapper(1) as bus:
            bus.write_i2c_block_data(self.address, 0x10, 0x00)
            return bus.read_byte(self.address)

    def get_bcr1_amps_a(self):
        with SMBusWrapper(1) as bus:
            bus.write_i2c_block_data(self.address, 0x10, 0x01)
            return bus.read_byte(self.address)

    def get_bcr1_amps_b(self):
        with SMBusWrapper(1) as bus:
            bus.write_i2c_block_data(self.address, 0x10, 0x02)
            return bus.read_byte(self.address)

    def get_battery_bus_volts(self):
        with SMBusWrapper(1) as bus:
            bus.write_i2c_block_data(self.address, 0x10, 0x23)
            return bus.read_byte(self.address)

    def set_modules(self, dictionary: dict):
        self.modules = dictionary

    def start(self):
        # self.bus = smbus.SMBus(1)
        self.logger = logging.getLogger("EPS")
        # NOTE: Feels like the ThreadHandler is not really used at all.
        # self.t2 = ThreadHandler(target=partial(board_check),
        #     name="eps-board_check", parent_logger=self.logger)
