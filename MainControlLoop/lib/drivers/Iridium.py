from enum import Enum
from serial import Serial

from MainControlLoop.lib.devices.device import Device


class IridiumCommand(Enum):
    TEST_IRIDIUM = 'AT'
    GEOLOCATION = 'AT-MSGEO'
    ACTIVE_CONFIG = 'AT+V'
    CHECK_REGISTRATION = 'AT+SBDREG?'
    PHONE_MODEL = 'AT+CGMM'
    PHONE_REVISION = 'AT+CGMR'
    PHONE_IMEI = 'AT+CSGN'
    CHECK_NETWORK = 'AT-MSSTM'  # FIXME: Iridium documentation says this is for system time?
    SHUT_DOWN = 'AT*F'

    # FIXME: cannot be tested until patch antenna is working
    # following commands probably need to be retested once patch antenna is fixed

    SEND_SMS = 'AT+CMGS='
    SIGNAL = 'AT+CSQ'
    SBD_RING_ALERT_ON = 'AT+SBDMTA=1'
    SBD_RING_ALERT_OFF = 'AT+SBDMTA=0'
    BATTERY_CHECK = 'AT+CBC=?'
    CALL_STATUS = 'AT+CLCC=?'
    SOFT_RESET = 'ATZn'


class Iridium(Device):
    PORT = '/dev/serial0'
    BAUDRATE = 19200

    def __init__(self):
        super().__init__('Iridium')
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
                self.serial.flush()
                return True
            except:
                return False

        if self.serial.is_open:
            return True

        try:
            self.serial.open()
            self.serial.flush()
            return True
        except:
            return False

    def write(self, message: str) -> bool:
        """
        Write a message to the serial port.
        :param message: (str) Message to write
        :return: (bool) if the serial write worked
        """

        if not self.functional():
            return False
     
        message = message + "\r\n"
        try:
            self.serial.write(message.encode("UTF-8"))
        except:
            return False

        return True

    def write_command(self, command: IridiumCommand) -> bool:
        """
        Writes one of the Iridium commands to the serial port
        :param command: (IridiumCommand) Command to write
        :return: (bool) if the serial write worked
        """

        if type(command) != IridiumCommand:
            return False

        if not self.functional():
            return False

        command_str = command.value + "\r\n"
        try:
            self.serial.write(command_str.encode("UTF-8"))
        except:
            return False

        return True

    def read(self) -> (bytes, bool):
        """
        Reads in as many available bytes as it can if timeout permits.
        :return: (byte) bytes read from Iridium, whether or not the write worked
        """
        output = bytes()
        for loop in range(50):

            try:
                next_byte = self.serial.read(size=1)
            except:
                return None, False

            if next_byte == bytes():
                break

            output += next_byte

        return output, True

    def reset(self):
        raise NotImplementedError

    def enable(self):
        raise NotImplementedError

    def disable(self):
        raise NotImplementedError
