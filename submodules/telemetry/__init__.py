import base64
import collections
import logging
from functools import partial
from threading import Lock

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

general_queue = collections.deque()
log_stack = collections.deque()
err_stack = collections.deque()

packet_lock = Lock()

def enqueue(message: str) -> None:
    """
    Enqueue a message onto the general queue, to be processed later by thread decide()
    :param message: The message to push onto general queue
    :return: Nothing
    """
    general_queue.append(message)

@command("telem_dump")
def dump(radio='aprs') -> None:
    """
    Concatenates packets to fit in max_packet_size (defined in config) and send through the radio, removing the
    packets in the process
    :param radio: Radio to send telemetry through, either "aprs" or "iridium"
    :return None
    """
    global packet_lock, log_stack, err_stack
    squishedpackets = ""

    # with packet_lock:
    #     while len(log_stack) + len(err_stack) > 0:
    #         if
    #
    #         radio_output.send(squishedpackets, radio)
    #         squishedpackets = ""

    #TODO: implement


@command("telem_clear")
def clear_buffers() -> None:
    """
    Clear the telemetry buffers - clearing general_queue, the log, and error stacks.
    :return: Nothing
    """
    global packet_lock, log_stack, err_stack, general_queue
    with packet_lock:
        general_queue.clear()
        log_stack.clear()
        err_stack.clear()


def decide() -> None:
    """
    A thread method to constantly check general_queue for messages and process them if there are any.
    :return: Nothing
    """
    global packet_lock
    while True:
        if len(general_queue) > 0:
            with packet_lock:
                message = general_queue.popleft()
                if len(message) < 5:    # Messages have to be longer than five characters because the first four
                                        # characters have to identify the type of message
                    logger.error("Message too short for it to be a valid message.")
                else:
                    if message[0:4] == "CMD$":
                        command_ingest.enqueue(message[4:])
                    elif message[0:4] == "ERR!":
                        err_stack.append(message)
                    elif message[0:4] == "LOG&":
                        log_stack.append(message)
                    else:   # Shouldn't execute (enqueue() should catch it) but here just in case
                        logger.error("Message prefix invalid.")


def start():
    """
    Starts the telemetry send thread
    """
    threadDecide = ThreadHandler(target=partial(decide()),
                       name="telemetry-decide")
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
