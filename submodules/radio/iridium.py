import logging
from threading import Lock
from functools import partial

from . import Radio
from core import ThreadHandler

from serial import Serial


class Iridium(Radio):

    def __init__(self, config):
        """
        Assumes Iridium is in low power mode on start. Sets up class fields.
        :param config: the config dictionary loaded from config_default.yml
        """
        self.config = config
        self.modules = dict()

        self.logger = logging.getLogger("IRIDIUM")
        self.read_lock = Lock()

        self.serial = None
        self.listen_thread = ThreadHandler(target=partial(self.listen), name="iridium-listen",
                                           parent_logger=self.logger)

    def start(self):
        """
           Opens the Iridium serial port and starts the listening thread.
           Assumes enough power is present therefore the tty port exists.
           If the Iridium check fails, it raises an error
        """

        self.serial = Serial(self.config['iridium']['serial_port'], baudrate=19200, timeout=30)
        self.serial.flush()

        if self.check(5):
            self.logger.debug("Iridium Check Successful")
        else:
            raise RuntimeError('Iridium Check Failed')

    def enter_low_power_mode(self):
        """
        Enters the Iridium into low power mode.
        Closes the serial port and pauses the listening thread
        Assumes Iridium is in normal mode
        """
        self.listen_thread.pause()
        self.serial.close()

    def enter_normal_mode(self):
        """
        Enters the Iridium into normal mode.
        Re-opens the serial port and resumes the listening thread
        Assumes Iridium is in low power mode.
        """

        self.serial.open()
        self.listen_thread.resume()

    def set_modules(self, modules):
        self.modules = modules

    def has_modules(self):
        return len(self.modules) is not 0

    def write_to_serial(self, command: str) -> (str, bool):
        """
        Write a command to the serial port.

        :param command: Command to write
        :return: (str, boolean) response text, boolean if error or not
        """

        if not self.serial.is_open:
            return 'ERROR', False

        # Remove unnecessary newlines that cut off the full command
        command = command.replace("\r\n", "")
        # Add the newline character to the end of the command
        command = command + "\r\n"

        # Encode the message with utf-8, write to serial
        self.serial.write(command.encode('UTF-8'))

        response = ""  # Received response
        self.read_lock.acquire()
        while ("OK" or "ERROR") not in response:  # Wait to get the 'OK' or 'ERROR' from Iridium
            if not self.serial.is_open:
                return 'ERROR', False
            response += self.serial.read().decode('UTF-8')  # Append contents of serial
        self.read_lock.release()

        # Determine if an "OK" or an "ERROR" was received
        if "OK" in response:  # "OK"
            response = response.replace("OK", "").strip()

            self.serial.flush()  # Flush the serial
            return response, True
        else:  # "ERROR"
            response = response.replace("ERROR", "").strip()
            self.serial.flush()  # Flush the serial
            return response, False

    def wait_for_signal(self):
        """
        Wait for the Iridium to establish a connection with the constellation.
        """
        if not self.serial.is_open:
            return
        response = 0
        while response == 0:
            response = int(self.write_to_serial("AT+CSQ")[0].split(":")[1])

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
        response = int(self.write_to_serial("AT+SBDREG?")[0].split(":")[1])

        # `response` should be 2, which means the Iridium is registered
        while num_checks > 0:  # Recheck the Iridium for `num_checks` number of times
            if response == 2:  # Check succeeded
                return True
            else:  # Check failed, retry
                response = int(self.write_to_serial("AT+SBDREG?")[0].split(":")[1])
                num_checks -= 1
        return False  # Check failed all times, return False

    def retrieve(self) -> str:
        """
        Retrieve the content of a message that is Mobile Terminated (MT).
        :return: Text content of the message, empty string if failed or no message to retrieve
        """

        self.wait_for_signal()

        # "Sync" with the GSS, retrieving and sending messages
        sync = self.write_to_serial("AT+SBDIXA")
        if not sync[1]:
            return ''

        sync_resp = sync[0]
        sync_resp_list = sync_resp.strip(",")

        if sync_resp_list[2] == 1:  # Message successfully received
            message = self.write_to_serial("AT+SBDRT")
            if not message[1]:
                return ''
            return message[0]  # Return the actual message content
        else:
            return ""  # Return nothing; either there was no message or retrieval failed

    def listen(self):
        """
        Listen for an SBD ring.
        If a ring is present, retrieve the message, and dispatch it to *command_ingest.*
        This function is meant to be run in a Thread.
        """

        # Turn SBD ring alerts on
        self.write_to_serial("AT+SBDMTA=1")

        while True:  # Continuously listen for rings
            if not self.has_modules:
                # Modules not set yet
                continue

            if not self.serial.is_open:
                # Low power mode
                continue

            # Wait for `read_lock` to be released, implies loop is run every 5 seconds minimum
            acquired_read_lock = self.read_lock.acquire(timeout=5)
            if acquired_read_lock:

                ring = b''
                port_closed = False
                while not ring.endswith(b'\n'):  # While EOL hasn't been sent

                    if not self.serial.is_open:
                        port_closed = True
                        break

                    result = self.serial.read()
                    ring += result

                if port_closed:
                    self.logger.debug('PORT GOT CLOSED WHILE READING LINE')
                    continue

                ring = ring.decode('utf-8')

                self.read_lock.release()
                self.logger.debug("Got SBDRING")

                if "SBDRING" in ring:
                    message = self.retrieve()
                    self.logger.debug(f"Message was {message}")

                    if message:  # Evaluates to True if message not empty
                        self.logger.debug(message)
                        if 'telemetry' in self.modules:
                            telemetry = self.modules['telemetry']
                            telemetry.enqueue(message)

    def send(self, message):
        """
        Send a message using the Iridium network.
        :param message: The message to send in plain text
        :return: True if message was sent, False if not
        """

        self.wait_for_signal()
        # Prepare message
        response_write = self.write_to_serial("AT+SBDWT=" + message)
        if not response_write[1]:  # Message write timed out
            return False

        self.wait_for_signal()
        # Send message
        response_sbdi = self.write_to_serial("AT+SBDI")
        if not response_sbdi[1]:
            return False

        response_sbdi_array = response_sbdi[0].split(":")[1].strip().split(",")  # Array of SBDI response

        if response_sbdi_array[0] == 2:  # Index 0 holds the success code
            return True
        else:
            return False
