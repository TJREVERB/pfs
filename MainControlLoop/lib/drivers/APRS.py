from time import sleep
from serial import Serial

from MainControlLoop.lib.devices import Device


class APRS(Device):
    PORT = '/dev/ttyACM0'
    DEVICE_PATH = '/sys/devices/platform/soc/20980000.usb/buspower'
    BAUDRATE = 19200

    def __init__(self):
        super().__init__("APRS")
        self.serial: Serial = None

    def flush(self):
        """
        Clears the serial buffer
        :return: (None)
        """
        self.serial.flushInput()
        self.serial.flushOutput()

    def functional(self) -> bool:
        """
        Checks the state of the serial port (initializing it if needed)
        :return: (bool) serial connection is working
        """
        if self.serial is None:
            try:
                self.serial = Serial(port=self.PORT, baudrate=self.BAUDRATE, timeout=1)
                self.flush()
                return True
            except:
                return False

        if self.serial.is_open:
            return True

        try:
            self.serial.open()
            self.flush()
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

    def read(self) -> (bytes, bool):
        """
        Reads in as many available bytes as it can if timeout permits (terminating at a \n).
        :return: (byte) bytes read from APRS, whether or not the write worked
        """
        if not self.functional():
            return None, False

        output = bytes()
        for loop in range(50):
            try:
                next_byte = self.serial.read(size=1)
            except:
                return None, False

            if next_byte == bytes():
                break

            output += next_byte
            if next_byte == '\n'.encode('utf-8'):
                break

        return output, True

    def reset(self):
        with open(self.DEVICE_PATH, 'w') as bus_power:
            bus_power.write('0')
            bus_power.close()
        sleep(10)
        with open(self.DEVICE_PATH, 'w') as bus_power:
            bus_power.write('0')
            bus_power.close()
        sleep(5)

    def enable(self):
        raise NotImplementedError

    def disable(self):
        raise NotImplementedError
