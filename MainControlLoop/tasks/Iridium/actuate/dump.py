from MainControlLoop.lib.drivers.Iridium import Iridium
from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry, ErrorFlag


class IridiumDumpActuateTask:
    def __init__(self, iridium: Iridium, state_field_registry: StateFieldRegistry):
        self.iridium: Iridium = iridium
        self.state_field_registry: StateFieldRegistry = state_field_registry
        self.run = False
        self.dump: list = []

    def set_dump(self, messages: list):
        if not isinstance(messages, list):
            return

        for message in messages:
            if not isinstance(message, str):
                return

        self.dump = messages

    def execute(self):
        if not self.run:
            return

        self.run = False
        if len(self.dump) == 0:
            return

        for portion in self.dump:
            success = self.iridium.write(portion)
            if not success:
                self.state_field_registry.raise_flag(ErrorFlag.IRIDIUM_FAILURE)
                self.dump = []
                return

        self.dump = []
