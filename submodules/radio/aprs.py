import logging
from functools import partial
from time import time, sleep

from . import Radio
from core import ThreadHandler

from serial import Serial


class APRS(Radio):

    def __init__(self, config):
        """
        Assumes APRS is in low power mode on start. Sets up class fields.
        :param config: the config dictionary loaded from config_default.yml
        """

        self.config = config
        self.modules = {}

        self.logger = logging.getLogger("APRS")
        self.last_telem_time = time()
        self.last_message_time = time()

        self.modules = dict()
        self._has_modules = False

        self.serial = None
        self.listen_thread = ThreadHandler(target=partial(self.listen), name="aprs-listen", parent_logger=self.logger)

    def start(self):
        """
        Opens the APRS serial port and starts the listening thread.
        Assumes enough power is present therefore the tty port exists.
        """
        self.serial = Serial(self.config['aprs']['serial_port'], 19200)
        self.listen_thread.start()

    def enter_low_power_mode(self):
        """
        Enters the APRS into low power mode.
        Closes the serial port and pauses the listening thread
        Assumes APRS is in normal mode
        """
        self.listen_thread.pause()
        self.serial.close()

    def enter_normal_mode(self):
        """
        Enters the APRS into normal mode.
        Re-opens the serial port and resumes the listening thread
        Assumes APRS is in low power mode.
        """

        self.serial.open()
        self.listen_thread.resume()

    def set_modules(self, modules):
        self.modules = modules
        self._has_modules = True

    def parse_aprs_packet(self, packet: str) -> str:
        """
        Given a raw radio packet, strip the APRS junk off of it and make it into pure data.
        :param packet: Input data packet to process.
        :return: The pure data with all APRS wrappers removed.
        """
        raw_packet = str(packet)
        self.logger.debug("From APRS: " + raw_packet)
        header_index = raw_packet.find(':')
        telemetry_heartbeat_header = raw_packet.find('T#')

        if header_index == -1:
            if telemetry_heartbeat_header == 0:
                # Telemetry Packet: APRS special case
                self.logger.debug('APRS telemetry heartbeat received')
                return raw_packet

            self.logger.error("Incomplete APRS header!")
            # Empty strings will not be enqueued to telemetry
            return ''

        header = raw_packet[:header_index]
        self.logger.debug("header: " + header)
        data = raw_packet[header_index + 1:]

        if len(data) == 0:
            self.logger.warning("Empty packet body! Will not be queued to telemetry")

        self.logger.debug("Body: " + data)
        return data

    def listen(self):
        """
        Read messages from serial. If a command is received, send it to `telemetry`
        Run via ThreadHandler listen_thread
        """
        while True:
            if not self._has_modules:
                # Modules not set yet
                continue

            if not self.serial.is_open:
                # Low power mode
                continue

            line = b''
            port_closed = False
            while not line.endswith(b'\n'):  # While EOL hasn't been sent

                if not self.serial.is_open:
                    port_closed = True
                    break

                result = self.serial.read()
                line += result

            if port_closed:
                self.logger.debug('PORT GOT CLOSED WHILE READING LINE')
                continue

            self.logger.debug("GOT SOMETHING")

            line = line.decode('utf-8')
            self.last_message_time = time()
            if 'T#' in line:
                self.last_telem_time = time()

            # Parse the line
            parsed_message = self.parse_aprs_packet(line)

            if parsed_message:
                if 'telemetry' in self.modules:
                    telemetry = self.modules['telemetry']
                    telemetry.enqueue(parsed_message)

    def send(self, message):
        """
        Write packet via serial. All concurrency issues should be handled by a higher packages.
        :param message: Message to send to the APRS.
        """

        self.last_message_time = time()
        self.serial.write((message + '\n').encode("utf-8"))  # Send the message
        sleep(1)
