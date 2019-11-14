import logging
from collections import deque as queue
from core import ThreadHandler
from functools import partial
from helpers.error import Error
from helpers.log import Log


class CommandIngest:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger("CI")
        self.modules = {}

        self.registered_commands = {}
        self.general_queue = queue()

        self.processes = {
            "dispatch": ThreadHandler(
                target=partial(self.dispatch)
            )
        }

    def set_modules(self, dependencies):
        self.modules = dependencies

    def has_module(self, module_name):
        return module_name in self.modules and self.modules[module_name] is not None

    def dispatch(self):
        while True:
            body = self.general_queue.pop()

            if "CMD$" in body:
                cmd = [part for part in body[body.find("$") + 1:].split(";") if part]
                try:
                    module, func = cmd[0], cmd[1]
                except IndexError:
                    pass #TODO: Invalid command report as such
                if self.validate_func(module, func):
                    try:
                        getattr(self.modules[module], func)()
                        self.send_through_aprs(f"CMDSUC: Command {cmd} executed successfully")
                        if self.has_module("telemetry"):
                            self.modules["telemetry"].enqueue(Log()) #TODO: ADD LOG
                        else:
                            raise RuntimeError("[command_ingest]:[telemetry] not found")
                    except Exception as e:
                        self.send_through_aprs(f"CMDERR: Command {cmd} failed with {e}")
            else:
                continue

    def enqueue(self, cmd):
        self.general_queue.append(cmd)

    def validate_func(self, module, func):
        if module not in self.modules:
            self.send_through_aprs(f"CMDERR: Module not found")
            return False
        if self.has_module(module):
            raise RuntimeError(f"[command_ingest]:[{module}] not found")
        if hasattr(module, func):
            self.send_through_aprs(f"CMDERR: Function {func} not found in {module}")
            return False
        return True

    def send_through_aprs(self, message):
        if self.has_module("aprs"):
            self.modules["aprs"].send(message) #FIXME FORMATTING
        else:
            raise RuntimeError("[aprs] not found")

    def start(self):
        for process in self.processes:
            self.processes[process].start()
