from enum import Enum

from MainControlLoop.lib.devices import Device

from smbus2 import SMBus


class EPSRegister(Enum):
    # TODO: Populate with actual register values
    PDM_STATUS = 0x0E


class EPS(Device):

    def __init__(self):
        Device.__init__(self, "EPS")
        self.bus = SMBus()
        self.bus_name = '/dev/i2c-1'
        self.address = 0x57

    def is_open(self):
        return self.bus.fd is not None

    def write_i2c_block_response(self, register: EPSRegister, data):
        if type(register) != EPSRegister:
            return

        self.write_i2c_block_data(register, data)
        return self.read_byte()

    def write_byte_response(self, register: EPSRegister, value):
        if type(register) != EPSRegister:
            return

        self.write_byte_data(register, value)
        return self.read_byte()

    def read_byte_data(self, register: EPSRegister):
        if type(register) != EPSRegister:
            return

        self.bus.open(self.bus_name)
        next_byte = self.bus.read_byte_data(self.address, register.value)
        self.bus.close()
        return next_byte

    def read_byte(self):
        self.bus.open(self.bus_name)
        next_byte = self.bus.read_byte(self.address)
        self.bus.close()
        return next_byte

    def write_i2c_block_data(self, register: EPSRegister, data):
        if type(register) != EPSRegister:
            return

        self.bus.open(self.bus_name)
        self.bus.write_i2c_block_data(self.address, register.value, data)
        self.bus.close()

    def write_byte_data(self, register: EPSRegister, value):
        if type(register) != EPSRegister:
            return

        self.bus.open(self.bus_name)
        self.bus.write_byte_data(self.address, register.value, value)
        self.bus.close()

    def functional(self):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def disable(self):
        raise NotImplementedError

    def enable(self):
        raise NotImplementedError
