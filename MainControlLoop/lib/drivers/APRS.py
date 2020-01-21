from serial import Serial, SerialException
from time import sleep

from MainControlLoop.lib.devices import Device


class APRS(Device):

    def __init__(self):
        super().__init__("aprs")
        self.serial: Serial = None
        self.port: str = '/dev/ttyACM0'
        self.baudrate: int = 9600

    def functional(self) -> bool:
        """
        Checks the state of the serial port (initializing it if needed)
        :return: (bool) serial connection is working
        """
        if self.serial is None:
            try:
                self.serial = Serial(port=self.port, baudrate=self.baudrate, timeout=1)
                return True
            except SerialException:
                # FIXME: for production any and every error should be caught here
                return False

        if self.serial.is_open:
            return True

        try:
            self.serial.open()
            return True
        except SerialException:
            # FIXME: for production any and every error should be caught here
            return False

    def write(self, message: str) -> bool:
        """
         Writes the message to the APRS radio through the serial port
        :param message: (str) message to write
        :return: (bool) response, whether or not the write worked
        """
        if not self.functional():
            return False

        self.serial.write((message + "\n").encode("utf-8"))
        sleep(1)   # TODO: test if this wait is necessary
        return True

    def read(self) -> bool or bytes:
        """
        Reads in a maximum of one byte if timeout permits.
        :return: (byte) byte read from Iridium
        """
        if not self.functional():
            return False

        return self.serial.read(size=1)

    def reset(self):
        # TODO: implement the power-cycle hard reset
        raise NotImplementedError

    def enable(self):
        # TODO: figure out what precautions should be taken in enable
        try:
            self.serial.open()
        except SerialException:
            # FIXME: for production any and every error should be caught here
            pass

    def disable(self):
        # TODO: figure out what precautions should be taken in disable
        try:
            self.serial.close()
        except SerialException:
            # FIXME: for production any and every error should be caught here
            pass
