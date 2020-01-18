from serial import Serial, SerialException
from time import sleep


class APRS_Driver:

    def __init__(self):
        self.serial: Serial = None
        self.port = '/dev/ttyACM0'
        self.baudrate = 9600

    def serial_safe(self):
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
        return False

    def write(self, message: str):
        if not self.serial_safe():
            return False

        self.serial.write((message + "\n").encode("utf-8"))
        sleep(1)   # FIXME: test if this wait is necessary

    def read(self):
        if not self.serial_safe():
            return False

        return self.serial.read(size=1)
