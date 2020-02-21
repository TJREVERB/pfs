from smbus2 import SMBus

from MainControlLoop.lib.devices import Device

from enum import Enum


class AntennaDeployerRegister(Enum):
    RESET = 0xAA
    ARM = 0xAD
    DISARM = 0xAC
    DEPLOY_ANTENNA_1 = 0xA1
    DEPLOY_ANTENNA_2 = 0xA2
    DEPLOY_ANTENNA_3 = 0xA3
    DEPLOY_ANTENNA_4 = 0xA4  # TODO: documentation says deploy methods need a parameter, figure out if this is the register parameter for i2c call


class AntennaDeployer(Device):
    BUS_NAME = '/dev/i2c-2'
    ADDRESS = 0x58

    def __init__(self):
        super().__init__("antenna_deployer")
        self.bus = SMBus()

    def write_i2c_block_response(self, register: AntennaDeployerRegister, data) -> bytes or None:
        if type(register) != AntennaDeployerRegister:
            return

        self.write_i2c_block_data(register, data)
        return self.read_byte()

    def write_byte_response(self, register: AntennaDeployerRegister, value) -> bytes or None:
        if type(register) != AntennaDeployerRegister:
            return

        self.write_byte_data(register, value)
        return self.read_byte()

    def read_byte_data(self, register: AntennaDeployerRegister) -> bytes or None:
        if type(register) != AntennaDeployerRegister:
            return

        self.bus.open(self.BUS_NAME)
        next_byte = self.bus.read_byte_data(self.ADDRESS, register.value)
        self.bus.close()
        return next_byte

    def read_byte(self) -> bytes or None:
        self.bus.open(self.BUS_NAME)
        next_byte = self.bus.read_byte(self.ADDRESS)
        self.bus.close()
        return next_byte

    def write_i2c_block_data(self, register: AntennaDeployerRegister, data):
        if type(register) != AntennaDeployerRegister:
            return

        self.bus.open(self.BUS_NAME)
        self.bus.write_i2c_block_data(self.ADDRESS, register.value, data)
        self.bus.close()

    def write_byte_data(self, register: AntennaDeployerRegister, data):
        if type(register) != AntennaDeployerRegister:
            return

        self.bus.open(self.BUS_NAME)
        self.bus.write_byte_data(self.ADDRESS, register.value, data)
        self.bus.close()

    def deploy(self, register: AntennaDeployerRegister):
        self.write_byte_data(register, register.ARM)
        self.write_byte_data(register, register.DEPLOY_ANTENNA_1)
        self.write_byte_data(register, register.DEPLOY_ANTENNA_2)
        self.write_byte_data(register, register.DEPLOY_ANTENNA_3)
        self.write_byte_data(register, register.DEPLOY_ANTENNA_4)

    def functional(self):
        """
        :return: (bool) i2c file opened by SMBus
        """
        return self.bus.fd is not None

    def reset(self):
        """
        Resets the Microcontroller on the ISIS Antenna Deployer
        :return: (bool) no error
        """
        try:
            self.bus.open(self.BUS_NAME)
        except:
            return False
        self.bus.write_byte(self.ADDRESS, AntennaDeployerRegister.RESET)

    def disable(self):
        """
        Disarms the ISIS Antenna Deployer
        """
        try:
            self.bus.open(self.BUS_NAME)
        except:
            return False
        self.bus.write_byte(self.ADDRESS, AntennaDeployerRegister.DISARM)

    def enable(self):
        """
        Arms the ISIS Antenna Deployer
        """
        try:
            self.bus.open(self.BUS_NAME)
        except:
            return False
        self.bus.write_byte(self.ADDRESS, AntennaDeployerRegister.ARM.value)
