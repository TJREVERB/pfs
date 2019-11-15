from submodules import Submodule
from core import ThreadHandler

from collections import deque as queue
from functools import partial


class CommandIngest(Submodule):
    def __init__(self, config):
        Submodule.__init__(self, "command_ingest", config)
        self.general_queue = queue()

        self.processes = {
            "dispatch": ThreadHandler(
                target=partial(self.dispatch),
                name="command_ingest_dispatch",
                parent_logger=self.logger,
            )
        }

    def dispatch(self):
        while True:
            body = self.general_queue.pop()
            if "CMD$" in body:
                cmd = [part for part in body[body.find("$") + 1:].split(";") if part]
                try:
                    module, func = cmd[0], cmd[1]
                except IndexError:
                    self.send_through_aprs(f"CMDERR: Unable to parse Commnd {cmd}")
                    continue
                if self.validate_func(module, func):
                    try:
                        getattr(self.modules[module], func)()
                        self.send_through_aprs(f"CMDSUC: Command {cmd} executed successfully")
                    except Exception as e:
                        self.send_through_aprs(f"CMDERR: Command {cmd} failed with {e}")

    def enqueue(self, cmd):
        self.general_queue.append(cmd)

    def validate_func(self, module, func):
        if module not in self.modules:
            self.send_through_aprs(f"CMDERR: Module not found")
            return False
        if not self.has_module(module):
            raise RuntimeError(f"[{self.name}]:[{module}] not found")
        if hasattr(module, func):
            self.send_through_aprs(f"CMDERR: Function {func} not found in {module}")
            return False
        return True

    def send_through_aprs(self, message):
        self.get_module_or_raise_error("aprs").send(f"{message}")  # FIXME FORAMTTING

    def enter_low_power_mode(self):  # TODO: WILL IMPLEMENT IN CYCLE 2
        pass

    def enter_normal_mode(self):  # TODO: WILL IMPLEMENT IN CYCLE 2
        pass