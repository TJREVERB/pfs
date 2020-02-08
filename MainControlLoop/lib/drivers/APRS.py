from serial import Serial
from time import sleep
import os

from MainControlLoop.lib.devices import Device


class APRS(Device):
    PORT = '/dev/ttyACM0'
    BAUDRATE = 19200

    def __init__(self):
        super().__init__("APRS")
        self.serial: Serial = None

    def functional(self) -> bool:
        """
        Checks the state of the serial port (initializing it if needed)
        :return: (bool) serial connection is working
        """
        if self.serial is None:
            try:
                self.serial = Serial(port=self.PORT, baudrate=self.BAUDRATE, timeout=1)
                return True
            except:
                return False

        if self.serial.is_open:
            return True

        try:
            self.serial.open()
            return True
        except:
            return False

    def write(self, message: str) -> bool:
        """
         Writes the message to the APRS radio through the serial port
        :param message: (str) message to write
        :return: (bool) whether or not the write worked
        """
        if not self.functional():
            return False

        try:
            self.serial.write((message + "\n").encode("utf-8"))
        except:
            return False

        return True

    def read(self) -> bool or bytes:
        """
        Reads in a maximum of one byte if timeout permits.
        :return: (byte) byte read from APRS, whether or not the write worked
        """
        if not self.functional():
            return None, False

        return self.serial.read(size=1), True

    def reset(self):
        os.system('echo 0 > /sys/devices/platform/soc/20980000.usb/buspower')
        sleep(10)
        os.system('echo 1 > /sys/devices/platform/soc/20980000.usb/buspower')
        sleep(5)

    def enable(self):
        raise NotImplementedError

    def disable(self):
        raise NotImplementedError
