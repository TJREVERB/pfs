from MainControlLoop.lib.drivers.APRS import APRS
from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry


class APRSDumpActuateTask:
    MAX_DUMP_LEN = 100  # FIXME: find actual maximum

    def __init__(self, aprs: APRS, state_field_registry: StateFieldRegistry):
        self.aprs: APRS = aprs
        self.state_field_registry: StateFieldRegistry = state_field_registry
        self.run = False
        self.dump: list = []

    def set_dump(self, message: str):
        if not isinstance(message, str):
            return

        # TODO: create a splitting format for the dump such that each piece is under the max len
        self.dump = [message]

    def execute(self):
        if not self.run:
            return

        if len(self.dump) == 0:
            self.run = False
            return

        for portion in self.dump:
            self.aprs.write(portion)

        self.dump = []
        self.run = False
