from MainControlLoop.lib.devices import Device

from smbus2 import SMBus


class EPS(Device):

    def __init__(self):
        Device.__init__(self, "EPS")
        self.bus = SMBus()
        self.bus_name = '/dev/i2c-1'
        self.address = 0x57

    def is_open(self):
        return self.bus.fd is not None

    def write_i2c_block_response(self, register, data):
        self.write_i2c_block_data(register, data)
        return self.read_byte()

    def write_byte_response(self, register, value):
        self.write_byte_data(register, value)
        return self.read_byte()

    def read_byte(self):
        self.bus.open(self.bus_name)
        next_byte = self.bus.read_byte(self.address)
        self.bus.close()
        return next_byte

    def write_i2c_block_data(self, register, data):
        self.bus.open(self.bus_name)
        self.bus.write_i2c_block_data(self.address, register, data)
        self.bus.close()

    def write_byte_data(self, register, value):
        self.bus.open(self.bus_name)
        self.bus.write_byte_data(self.address, register, value)
        self.bus.close()

    def functional(self):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def disable(self):
        raise NotImplementedError

    def enable(self):
        raise NotImplementedError
