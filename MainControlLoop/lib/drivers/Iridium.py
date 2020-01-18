from serial import Serial, SerialException
from time import sleep
from enum import Enum

from MainControlLoop.lib.devices.device import Device


class Commands(Enum):
    SIGNAL = 'AT+CSQ'
    CHECK_REGISTRATION = 'AT+SBDREG?'
    SBD_RING_ALERT_ON = 'AT+SBDMTA=1'
    SBD_RING_ALERT_OFF = 'AT+SBDMTA=0'
    TEST_IRIDIUM = 'AT'


class Iridium(Device):

    def __init__(self):
        self.serial: Serial = None
        self.port = '/dev/ttyACM1'
        self.baudrate = 9600
        Device.__init__(self, 'Iridium')

    def get_response(self, command):
        """
        Returns the response code in the command
        :param command: (str) command to look in
        :return: (int) response code
        """
        return int(self.write_to_serial(command)[0].split(":")[1])

    def write_to_serial(self, command: str) -> (str, bool):
        """
        Write a command to the serial port.
        :param command: (str) Command to write
        :return: (str, boolean) response text, boolean if error or not
        """

        if self.serial is None or not self.serial.is_open:
            return "ERROR", False

        # Remove unnecessary newlines that cut off the full command
        command = command.replace("\r\n", "")
        # Add the newline character to the end of the command
        command = command + "\r\n"

        # Encode the message with utf-8, write to serial
        self.serial.write(command.encode("UTF-8"))

        response = ""

        # Wait to get the 'OK' or 'ERROR' from Iridium
        while "OK" or "ERROR" not in response:
            if not self.serial.is_open:
                return "ERROR", False

            response += self.serial.read(size=1).decode("UTF-8")

        if "OK" in response:
            response = response.replace("OK", "").strip()
            self.serial.flush()  # Flush the serial
            return response, True

        # ERROR
        response = response.replace("ERROR", "").strip()
        self.serial.flush()
        return response, False

    def wait_for_signal(self):
        """
        Wait for the Iridium to establish a connection with the constellation.
        """
        if not self.serial.is_open:
            return
        response = 0
        while response == 0:
            response = self.get_response(Commands.SIGNAL.value)

    def check(self, num_checks: int) -> bool:
        """
        Check that the Iridium works and is registered.
        :param num_checks: (int) Number of times to check if the Iridium is registered (before it returns)
        :return: (bool) Check is successful
        """

        self.write_to_serial(Commands.TEST_IRIDIUM.value)

        self.wait_for_signal()

        # Check if current registration status of the Iridium `response` is 2
        response = self.get_response(Commands.CHECK_REGISTRATION.value)
        while num_checks > 0:
            if response == 2:
                self.write_to_serial(Commands.SBD_RING_ALERT_ON.value)
                return True

            response = self.get_response(Commands.CHECK_REGISTRATION.value)
            num_checks -= 1

        return False

    def functional(self):
        """
        Checks the state of the serial port (initializing it if needed)
        :return: (bool) serial connection is working
        """
        if self.serial is None:
            try:
                self.serial = Serial(port=self.port, baudrate=self.baudrate, timeout=1)
                self.serial.flush()
                return self.check(5)
            except SerialException:
                # FIXME: for production any and every error should be caught here
                return False
        if self.serial.is_open:
            return True
        return False

    def write(self, message: str):
        """
         Writes the message to the Iridium radio through the serial port
        :param message: (str) message to write
        :return: (str, bool) response, whether or not the write worked
        """
        if not self.functional():
            return '', False

        command = message  # FIXME: convert message into an Iridium command to send
        response, success = self.write_to_serial(command)
        sleep(1)  # TODO: test if this wait is necessary
        return response, success

    def read(self):
        """
        Reads in a maximum of one byte if timeout permits.
        :return: (byte) byte read from Iridium
        """
        if not self.functional():
            return False

        return self.serial.read(size=1)
