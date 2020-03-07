from serial import Serial
from enum import Enum

from MainControlLoop.lib.devices.device import Device


class Commands(Enum):
    TEST_IRIDIUM = 'AT'
    GEOLOCATION = 'AT-MSGEO'
    ACTIVE_CONFIG = 'AT+V'
    CHECK_REGISTRATION = 'AT+SBDREG?'
    PHONE_MODEL = 'AT+CGMM'
    PHONE_REVISION = 'AT+CGMR'
    PHONE_IMEI = 'AT+CSGN'
    CHECK_NETWORK = 'AT-MSSTM'
    SHUT_DOWN = 'AT*F'
    SIGNAL_QUAL = 'AT+CSQ'

    # FIXME: cannot be tested until patch antenna is working
    # following commands probably need to be retested once patch antenna is fixed

    SEND_SMS = 'AT+CMGS='
    SIGNAL = 'AT+CSQ'
    SBD_RING_ALERT_ON = 'AT+SBDMTA=1'
    SBD_RING_ALERT_OFF = 'AT+SBDMTA=0'
    BATTERY_CHECK = 'AT+CBC=?'
    CALL_STATUS = 'AT+CLCC=?'
    SOFT_RESET = 'ATZn'


class ResponseCode(Enum):
    OK = [b'O', b'K']
    ERROR = [c.encode('utf-8') for c in 'ERROR']


class Iridium(Device):
    PORT = '/dev/serial0'
    BAUDRATE = 19200

    def __init__(self):
        super().__init__('Iridium')
        self.serial: Serial = None

    def write(self, command: str) -> bool:
        """
        Write a command to the serial port.
        :param command: (str) Command to write
        :return: (bool) if the serial write worked
        """
        if not self.functional():
            return False
        # Add the newline character to the end of the command
        command = command + "\r\n"

        # Encode the message with utf-8, write to serial
        try:
            self.serial.write(command.encode("UTF-8"))
        except SerialException:
            return False

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

    def flush(self):
        """
        Clears the serial buffer
        :return: (None)
        """
        self.serial.flushInput()
        self.serial.flushOutput()

    def read(self) -> (bytes, bool):
        """
        Reads in a maximum of one byte if timeout permits.
        :return: (bytes, bool) bytes read from Iridium, success
        """
        if not self.functional():
            return None, False

        return self.serial.read(1), True

    def reset(self):
        """
        Resets the serial powers
        :return: (None)
        """
        raise NotImplementedError
