import logging
from functools import partial
from time import time, sleep

from . import Radio
from core import ThreadHandler
from core import Mode

from serial import Serial


class APRS(Radio):

    def __init__(self, config):
        """
        Assumes APRS is in low power mode on start. Sets up class fields.
        :param config: the config dictionary loaded from config_default.yml
        """

        self.config = config

        self.logger = logging.getLogger("APRS")
        self.last_telem_time = time()
        self.last_message_time = time()

        self.mode = Mode.LOW_POWER
        self.serial = None
        self.listen_thread = None

    def enter_low_power_mode(self):
        """
        Enters the APRS into low power mode
        Closes the serial port and pauses the listening thread
        """

        if self.listen_thread is not None:
            self.listen_thread.pause()

        if self.serial is not None:
            self.serial.close()

        self.mode = Mode.LOW_POWER

    def enter_normal_mode(self):
        """
        Enters the APRS into normal mode
        Opens the serial port and starts/resumes the listening thread
        """

        if self.serial is None:
            # First time normal mode is entered
            self.serial = Serial(self.config['aprs']['serial_port'], 19200)
        else:
            self.serial.open()

        if self.listen_thread is None:
            # First time normal mode is entered
            self.listen_thread = ThreadHandler(target=partial(self.listen), name="aprs-listen", parent_logger=self.logger)
            self.listen_thread.start()
        else:
            self.listen_thread.resume()

        self.mode = Mode.NORMAL

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
            if self.mode is Mode.LOW_POWER:
                continue

            line = b''
            while not line.endswith(b'\n'):  # While EOL hasn't been sent
                self.logger.debug("GOT SOMETHING")
                res = self.serial.readline()
                line += res
            line = line.decode('utf-8')
            self.last_message_time = time()
            if 'T#' in line:
                self.last_telem_time = time()

            # Parse the line
            parsed = self.parse_aprs_packet(line)

            if parsed:
                # TODO: Pass parsed to the telemetry object
                pass

    def send(self, message):
        """
        Put a packet in the APRS queue.  The APRS queue exists
        only to make sure that we don't send and receive at the
        same time.
        :param message: Message to send into the APRS queue.
        """

        # Wait until `message_spacing` seconds after the last received message
        while True:
            while time() - self.last_message_time < self.config['aprs']['message_spacing']:
                sleep(1)
            self.last_message_time = time()

            self.serial.write((message + '\n').encode("utf-8"))  # Send the message

            sleep(1)
