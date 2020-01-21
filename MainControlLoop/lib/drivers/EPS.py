from MainControlLoop.lib.devices import Device

from smbus2 import SMBus


class EPS(Device):

    def __init__(self):
        Device.__init__(self, "EPS")
        self.bus = SMBus()
        self.bus_name = '/dev/i2c-1'
        self.address = 0x57

    def functional(self):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def disable(self):
        raise NotImplementedError

    def enable(self):
        raise NotImplementedError
