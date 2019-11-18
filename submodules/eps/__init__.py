import logging
import time
import smbus
import yaml

from functools import partial

from smbus2 import SMBusWrapper
from submodules import telemetry

from submodules.submodule import Submodule
from helpers.log import Log
from helpers.error import Error
from helpers.threadhandler import ThreadHandler

class EPS(Submodule):
    
    def __init__(self, config):
        Submodule.__init__(self, name="eps", config=config)
        self.address = 0x57
        self.eps_dict = {'a':1, 'i2c':2, 'c':3, 'antenna':4, 'pi':5, 'iridium':6, 'aprs':7, 'h':8}

    def pin_on(self, device_name) -> bool:
        with SMBusWrapper(1) as bus:
            if device_name in self.eps_dict:
                PDM_val = self.eps_dict[device_name]
            else:
                message = "Device name \"{}\" INVALID. Aborting command.".format(device_name)
                self.logger.error(message)
                self.get_module_or_raise_error("telemetry").enqueue(Error(sys_name=self.name, msg=message))
                return False

            if self.get_PDM_status(device_name) == 1:
                message = "Pin {} ({}) is already ON.".format(self.eps_dict[device_name], device_name)
                self.logger.debug(message)  # Log to console for debugging
                self.get_module_or_raise_error("telemetry").enqueue(Log(sys_name=self.name, lvl="INFO", msg=message))  # Push to telemetry stack
                return True
            else:
                bus.write_byte_data(self.address, 0x12, PDM_val)  # Attempt to execute pin on

                if self.get_PDM_status(device_name) == 1:  # PDM is ON
                    message = "Pin {} ({}) communication successful. Pin is now ON.".format(
                        self.eps_dict[device_name], device_name)
                    self.logger.debug(message)
                    self.get_module_or_raise_error("telemetry").enqueue(Log(sys_name=self.name, lvl="INFO", msg=message))
                    return True
                else:  # Something is big broken
                    message = "Pin {} ({}) communication NOT successful. Pin is still OFF.".format(
                        self.eps_dict[device_name], device_name)
                    self.logger.error(message)
                    self.get_module_or_raise_error("telemetry").enqueue(Error(sys_name=self.name, msg=message))
                    return False

    def pin_off(self, device_name) -> bool:
        with SMBusWrapper(1) as bus:
            if device_name in self.eps_dict:
                PDM_val = self.eps_dict[device_name]
            else:
                message = "Device name \"{}\" INVALID. Aborting command.".format(device_name)
                self.logger.error(message)
                self.get_module_or_raise_error("telemetry").enqueue(Error(sys_name=self.name, msg=message))
                return False

            if self.get_PDM_status(device_name) == 0:
                message = "Pin {} ({}) is already OFF.".format(self.eps_dict[device_name], device_name)
                self.logger.debug(message)  # Log to console for debugging
                self.get_module_or_raise_error("telemetry").enqueue(Log(sys_name=self.name, lvl="INFO", msg=message))  # Push to telemetry stack
                return True
            else:
                bus.write_byte_data(self.address, 0x13, PDM_val)  # Attempt to execute pin off

                if self.get_PDM_status(device_name) == 0:  # PDM is OFF
                    message = "Pin {} ({}) communication successful. Pin is now OFF.".format(
                        self.eps_dict[device_name], device_name)
                    self.logger.debug(message)
                    self.get_module_or_raise_error("telemetry").enqueue(Log(sys_name=self.name, lvl="INFO", msg=message))
                    return True
                else:
                    message = "Pin {} ({}) communication NOT successful. Pin is still ON.".format(
                        self.eps_dict[device_name], device_name)
                    self.logger.error(message)
                    self.get_module_or_raise_error("telemetry").enqueue(Error(sys_name=self.name, msg=message))
                    return False

    def reboot_device(self, device_name, wait_after_off=10, wait_after_on=30):
        """
        :param wait_time_after_off: Time to wait after turning the device off
        :param wait_time_after_on: Time to wait before verifying the reboot was successful 
            (i.e. after turn on command)
        :return: Boolean representing whether or not the reboot was successful
        """
        # FIXME: Do we need a self.pin_off() or just pin_off()?
        if not self.pin_off(device_name):  # If it's still on? Maybe trying to see if pin_off() was successful?
            return False
        # TODO: All code below is unconverted
        message = "From Pin {} ({}) reboot: sleeping {} second(s) after turn off.".format(
            self.eps_dict[device_name], device_name, wait_after_off)
        self.logger.debug(message)
        self.get_module_or_raise_error("telemetry").enqueue(Log(sys_name=self.name, lvl="INFO", msg=message))
        time.sleep(wait_after_off)  # Wait for specified time

        if not self.pin_on(device_name):
            return False
        message = "From Pin {} ({}) reboot: sleeping {} second(s) after turn on.".format(
            self.eps_dict[device_name], device_name, wait_after_off)
        self.logger.debug(message)
        self.get_module_or_raise_error("telemetry").enqueue(Log(sys_name=self.name, lvl="INFO", msg=message))
        time.sleep(wait_after_off)

        if self.get_PDM_status(device_name) == 1:
            message = "Pin {} ({}) reboot successful.".format(self.eps_dict[device_name], device_name)
            self.logger.debug(message)
            self.get_module_or_raise_error("telemetry").enqueue(Log(sys_name=self.name, lvl="INFO", msg=message))
            return True
        else:
            message = "Pin {} ({}) reboot NOT successful. Recommend PDM status check in {} second(s).".format(
                self.eps_dict[device_name], device_name, wait_after_off)
            self.logger.error(message)
            self.get_module_or_raise_error("telemetry").enqueue(Error(sys_name=self.name, msg=message))
            return False

    def get_PDM_status(self, device_name):
        with SMBusWrapper(1) as bus:
            PDM_val = self.eps_dict[device_name]
            bus.write_byte_data(self.address, 0x0E, PDM_val)
            return bus.read_byte(self.address)

    def is_module_on(self, device_name) -> bool:
        if self.get_PDM_status(device_name) == 0:
            return False
        return True

    def get_board_status(self):
        with SMBusWrapper(1) as bus:
            return bus.read_byte_data(self.address, 0x01)

    def get_device_statuses(self) -> dict:
        temp_dict = dict()
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

    def start(self):
        self.bus = smbus.SMBus(1)
