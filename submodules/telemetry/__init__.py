import base64
import collections
import logging
from functools import partial
from threading import Lock
from time import sleep

from core.threadhandler import ThreadHandler
# from submodules import radio_output

# Log and error classes
from core import error, log

logger = logging.getLogger("TELEMETRY")


class Telemetry:
    def __init__(self, config):
        """
        Constructor method. Initializes variables
        :param config: Config variable passed in from core.
        """
        self.config = config
        self.modules = {}
        self.general_queue = collections.deque()  # initialize global variables
        self.log_stack = collections.deque()
        self.err_stack = collections.deque()
        self.packet_lock = Lock()
        self.logger = logging.getLogger("TELEMETRY")

    def set_modules(self, modules: {}) -> None:
        """
        Sets modules variable
        :param modules: Maps strings to classes, like {"telemetry": Telemetry()}
        :return: None
        """
        self.modules = modules

    def enqueue(self, message) -> None:
        """
        Enqueue a message onto the general queue, to be processed later by thread decide()
        :param message: The message to push onto general queue. Must be a log/error class
        or command (string - must begin with semicolon, see command_ingest's readme)
        :return None
        """
        if not ((type(message) is str and message[0] == ';') or type(message) is error.Error or type(
                message) is log.Log):   # check for valid types, error if invalid
            self.logger.error("Attempted to enqueue invalid message")
            return
        with self.packet_lock:
            self.general_queue.append(message)  # append to general queue

    def dump(self, radio='aprs') -> None:
        """
        Concatenates packets to fit in max_packet_size (defined in config) and send through the radio, removing the
        packets from the error and log stacks in the process
        :param radio: Radio to send telemetry through, either "aprs" or "iridium"
        :return None
        """
        squishedpackets = ""

        with self.packet_lock:
            while len(self.log_stack) + len(self.err_stack) > 0:    # while there's stuff to pop off
                next_packet = (self.err_stack[-1].to_string() if len(self.err_stack) > 0 else self.log_stack[-1].to_string())   # for the purposes of determining packet length
                while len(base64.b64encode((squishedpackets + next_packet).encode('ascii'))) < self.config["telemetry"]["max_packet_size"] and len(self.log_stack) + len(self.err_stack) > 0:
                    if len(self.err_stack) > 0: # prefer error messages over log messages
                        squishedpackets += self.err_stack.pop().to_string()
                    else:
                        squishedpackets += self.log_stack.pop().to_string()
                squishedpackets = base64.b64encode(squishedpackets.encode('ascii'))
                self.modules["aprs"].send(squishedpackets) # , radio) #FIXME currently just using APRS, what about radio_output?
                squishedpackets = ""

    def clear_buffers(self) -> None:
        """
        Clear the telemetry buffers - clearing general_queue, the log, and error stacks.
        :return: None
        """
        with self.packet_lock:
            self.general_queue.clear()
            self.log_stack.clear()
            self.err_stack.clear()

    def decide(self) -> None:
        """
        A thread method to constantly check general_queue for messages and process them if there are any.
        :return: None
        """
        while True:
            if len(self.general_queue) != 0:
                with self.packet_lock:
                    message = self.general_queue.popleft()
                    if type(message) is str and message[0] == ';':
                        self.modules["command_ingest"].enqueue(message)
                        # print("Running command_ingest.enqueue(" + message + ")")
                    elif type(message) is error.Error:
                        self.err_stack.append(message)
                    elif type(message) is log.Log:
                        self.log_stack.append(message)
                    else:  # Shouldn't execute (enqueue() should catch it) but here just in case
                        self.logger.error("Message prefix invalid.")
            sleep(1)

    def start(self) -> None:
        """
        Starts the telemetry send thread
        :return None
        """
        if self.config is None:
            raise RuntimeError("Config variable empty")

        threadDecide = ThreadHandler(target=partial(self.decide), name="telemetry-decide")  # start telemetry 'decide' thread
        threadDecide.start()

    # def enter_normal_mode() -> None:
    #     """
    #     Enter normal mode.
    #     :return: None
    #     """
    #     global state
    #     state = Mode.NORMAL
    #
    #
    # def enter_low_power_mode() -> None:
    #     """
    #     Enter low power mode.
    #     :return: None
    #     """
    #     global state
    #     state = Mode.LOW_POWER
    #
    #
    # def enter_emergency_mode() -> None:
    #     """
    #     Enter emergency mode.
    #     :return: None
    #     """
    #     global state
    #     state = Mode.EMERGENCY
