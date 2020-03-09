from enum import Enum

from MainControlLoop.lib.devices import Device

from smbus2 import SMBus


class EPSRegister(Enum):
    # TODO: Populate with actual register values
    PDM_STATUS = 0x0E


class EPS(Device):
    BUS_NAME = '/dev/i2c-1'
    ADDRESS = 0x57

    def __init__(self):
        super().__init__("EPS")
        self.bus = SMBus()

    def is_open(self) -> bool:
        return self.bus.fd is not None

    def write_i2c_block_response(self, register: EPSRegister, data) -> bytes or None:
        if type(register) != EPSRegister:
            return

        self.write_i2c_block_data(register, data)
        return self.read_byte()

    def write_byte_response(self, register: EPSRegister, value) -> bytes or None:
        if type(register) != EPSRegister:
            return

        self.write_byte_data(register, value)
        return self.read_byte()

    def read_byte_data(self, register: EPSRegister) -> bytes or None:
        if type(register) != EPSRegister:
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

    def write_i2c_block_data(self, register: EPSRegister, data):
        if type(register) != EPSRegister:
            return

        self.bus.open(self.BUS_NAME)
        self.bus.write_i2c_block_data(self.ADDRESS, register.value, data)
        self.bus.close()

    def write_byte_data(self, register: EPSRegister, value):
        if type(register) != EPSRegister:
            return

        self.bus.open(self.BUS_NAME)
        self.bus.write_byte_data(self.ADDRESS, register.value, value)
        self.bus.close()

    def functional(self):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def disable(self):
        raise NotImplementedError

    def enable(self):
        raise NotImplementedError
