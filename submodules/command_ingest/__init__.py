import logging
from inspect import signature
from collections import deque as queue
from core import ThreadHandler
from functools import partial
from helpers.error import Error


class CommandIngest:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger("CI")
        self.modules = {}

        self.total_received: int = 0
        self.total_errors: int = 0
        self.total_success: int = 0

        self.registered_commands = {}
        self.general_queue = queue()

        self.processes = {
            "dispatch": ThreadHandler(
                target=partial(self.dispatch)
            )
        }

    def set_modules(self, dependencies):
        self.modules = dependencies

    def dispatch(self):
        while True:
            body = self.general_queue.pop()

            # Get the individual parts of the message
            parts = [part for part in body.split(";") if part]
            command, arguments, checksum = parts[0], parts[1].split(","), parts[2]

            if self.generate_checksum(command) == checksum:
                associated = self.associate(command)
                if associated is not None:
                    associated_sig = signature(associated)
                    # Check num args and arg types

                    if not len(arguments) == len(associated_sig.parameters):
                        self.modules["telemetry"].enqueue(Error(sys_name="CI", msg="Incorrect number of arguments"))
                    try:
                        associated(*arguments)()
                    except:
                        self.modules["telemetry"].enqueue(Error(sys_name="CI", msg="Bad function"))
            else:
                self.modules["telemetry"].enqueue(Error(sys_name="CI", msg="Incorrect checksum"))

    def enqueue(self, cmd: str):
        self.general_queue.append(cmd)

    def generate_checksum(self, cmd: str):
        """
        Given a message body, generate its checksum
        :param cmd: Command to send.
        :return: Generated checksum for the message.
        """

        cmd_sum = sum([ord(x) for x in cmd])
        cmd_sum %= 26
        cmd_sum += 65
        self.logger.debug('CHECKOUT :' + chr(cmd_sum) + ";")
        return chr(cmd_sum)

    @staticmethod
    def associate(cmd: str):
        """
        Given a function name, return a decorator that registers that function.
        :return: Decorator that registers function.
        """

        valid_commands = {
            "test": lambda x, y: x + y}

        if cmd in valid_commands:
            return valid_commands.get(cmd)
        else:
            return None

    def start(self):
        for process in self.processes:
            self.processes[process].start()
