# This file is responsible for sending large volumes of data over the APRS radio
# call the instance method set_dump(messages: list) with a list of messages and then call the instance method execute() to send them over the APRS radio
# NOTE: the messages must each be shorter than MAX_DUMP_LEN

from MainControlLoop.lib.drivers.APRS import APRS
from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry, ErrorFlag


class APRSDumpActuateTask:
    MAX_DUMP_LEN = 256

    def __init__(self, aprs: APRS, state_field_registry: StateFieldRegistry):
        self.aprs: APRS = aprs
        self.state_field_registry: StateFieldRegistry = state_field_registry
        self.run = False
        self.dump: list = []

    def set_dump(self, messages: list):
        if not isinstance(messages, list):
            return

        for message in messages:
            if not isinstance(message, str):
                return
            if len(message) > self.MAX_DUMP_LEN:
                return

        self.dump = messages

    def execute(self):
        if not self.run:
            return

        self.run = False
        if len(self.dump) == 0:
            return

        for portion in self.dump:
            success = self.aprs.write(portion)
            if not success:
                self.state_field_registry.raise_flag(ErrorFlag.APRS_FAILURE)
                self.dump = []
                return

        self.dump = []
