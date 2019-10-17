import base64
import collections
import logging
from functools import partial
from threading import Lock
from time import sleep

from core.mode import Mode

from core import config
from core.threadhandler import ThreadHandler
from submodules import radio_output
from submodules import command_ingest

# Command Ingest - ability to register commands
from submodules.command_ingest import command

# Log and error classes
from core import error, log

logger = logging.getLogger("TELEMETRY")


def enqueue(message) -> None:

    """Enqueue a message onto the general queue, to be processed later by thread decide()
    :param message: The message to push onto general queue. Must be a log/error class
    or command (string - must begin with semicolon, see command_ingest's readme)
    :return None
    """
    global packet_lock, general_queue
    if not ((type(message) is str and message[0] == ';') or type(message) is error.Error or type(message) is log.Log):
        logger.error("Attempted to enqueue invalid message")
        return
    with packet_lock:
        general_queue.append(message)


def dump(radio='aprs') -> None:
    """
    Concatenates packets to fit in max_packet_size (defined in config) and send through the radio, removing the
    packets from the error and log stacks in the process
    :param radio: Radio to send telemetry through, either "aprs" or "iridium"
    :return None
    """
    global packet_lock, log_stack, err_stack
    squishedpackets = ""

    with packet_lock:
        while len(log_stack) + len(err_stack) > 0:
            next_packet = (err_stack[-1].to_string() if len(err_stack) > 0 else log_stack[-1].to_string())
            while len(base64.b64encode((squishedpackets + next_packet).encode('ascii'))) < config["telemetry"]["max_packet_size"] and len(log_stack) + len(err_stack) > 0:
                if len(err_stack) > 0:
                    squishedpackets += err_stack.pop().to_string()
                else:
                    squishedpackets += log_stack.pop().to_string()
            squishedpackets = base64.b64encode(squishedpackets.encode('ascii'))
            radio_output.send(squishedpackets, radio)
            squishedpackets = ""


def clear_buffers() -> None:
    """
    Clear the telemetry buffers - clearing general_queue, the log, and error stacks.
    :return: None
    """
    global packet_lock, log_stack, err_stack, general_queue
    with packet_lock:
        general_queue.clear()
        log_stack.clear()
        err_stack.clear()


def decide() -> None:
    """
    A thread method to constantly check general_queue for messages and process them if there are any.
    :return: None
    """
    global packet_lock, err_stack, log_stack, general_queue
    while True:
        if len(general_queue) != 0:
            with packet_lock:
                message = general_queue.popleft()
                if type(message) is str and message[0] == ';':
                    command_ingest.enqueue(message)
                    #print("Running command_ingest.enqueue(" + message + ")")
                elif type(message) is error.Error:
                    err_stack.append(message)
                elif type(message) is log.Log:
                    log_stack.append(message)
                else:  # Shouldn't execute (enqueue() should catch it) but here just in case
                    logger.error("Message prefix invalid.")
        sleep(1)


def start() -> None:
    """
    Starts the telemetry send thread
    :return None
    """
    global err_stack, log_stack, general_queue, packet_lock
    general_queue = collections.deque()  # initialize global variables
    log_stack = collections.deque()
    err_stack = collections.deque()
    packet_lock = Lock()

    threadDecide = ThreadHandler(target=partial(decide), name="telemetry-decide")  # start telemetry 'decide' thread
    threadDecide.start()


def enter_normal_mode() -> None:
    """
    Enter normal mode.
    :return: None
    """
    global state
    state = Mode.NORMAL


def enter_low_power_mode() -> None:
    """
    Enter low power mode.
    :return: None
    """
    global state
    state = Mode.LOW_POWER


def enter_emergency_mode() -> None:
    """
    Enter emergency mode.
    :return: None
    """
    global state
    state = Mode.EMERGENCY
