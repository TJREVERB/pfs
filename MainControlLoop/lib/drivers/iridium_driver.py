from serial import Serial, SerialException
from time import sleep


class IridiumDriver:

    def __init__(self):
        self.serial: Serial = None
        self.port = '/dev/ttyACM1'
        self.baudrate = 9600

    def get_response(self, command):
        return int(self.write_to_serial(command)[0].split(":")[1])

    def write_to_serial(self, command: str) -> (str, bool):
        """
        Write a command to the serial port.

        :param command: Command to write
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
            response = self.get_response('AT+CSQ')

    def check(self, num_checks: int) -> bool:
        """
        Check that the Iridium works and is registered.
        :param num_checks: Number of times to check if the Iridium is registered (before it returns)
        :return: True if check was successful, False if not
        """

        self.write_to_serial("AT")  # Test the Iridium

        self.wait_for_signal()

        # Get the current registration status of the Iridium
        # Return OK and end lines when they should be removed in write_to_serial
        response = self.get_response("AT+SBDREG?")

        # `response` should be 2, which means the Iridium is registered

        # Recheck the Iridium for `num_checks` number of times
        while num_checks > 0:
            # Check succeeded
            if response == 2:
                return True

            # Check failed, retry
            response = self.get_response("AT+SBDREG?")
            num_checks -= 1

        # Check failed all times, return False
        return False

    def serial_safe(self):
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
        if not self.serial_safe():
            return '', False

        command = message  # FIXME: convert message into an Iridium command to send =
        response, success = self.write_to_serial(command)
        sleep(1)   # TODO: test if this wait is necessary
        return response, success

    def read(self):
        if not self.serial_safe():
            return False

        return self.serial.read(size=1)
