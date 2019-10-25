import logging
from inspect import signature
from collections import deque as queue
from core import ThreadHandler
from functools import partial


class CommandIngest:

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger("CI")

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
                        # TODO: log error (incorrect num of args)
                        print("ERR: incorrect length")
                    try:
                        print("REACHED")
                        print(associated(*arguments))  # Actually run the command
                    except:
                        # TODO: send error immediately
                        print("ERR: bad function")
            else:
                # TODO: log that checksum is incorrect
                print("ERR: incorrect checksum")

    def enqueue(self, cmd: str):
        self.general_queue.append(cmd)

    def generate_checksum(self, cmd: str):
        """
        Given a message body, generate its checksum
        :param body: The body of the message.
        :return: Generated checksum for the message.
        """

        cmd_sum = sum([ord(x) for x in cmd])
        cmd_sum %= 26
        cmd_sum += 65
        self.logger.debug('CHECKOUT :' + chr(cmd_sum) + ";")
        return chr(cmd_sum)

    def associate(self, cmd: str):
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

