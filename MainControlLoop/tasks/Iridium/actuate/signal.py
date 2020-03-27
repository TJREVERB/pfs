from MainControlLoop.lib.drivers.Iridium import Iridium, IridiumCommand
from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry, ErrorFlag


class IridiumSignalStrengthActuateTask:
    def __init__(self, iridium: Iridium, state_field_registry: StateFieldRegistry):
        self.iridium: Iridium = iridium
        self.state_field_registry: StateFieldRegistry = state_field_registry
        self.run = False

    def execute(self):
        if not self.run:
            return

        self.run = False

        success = self.iridium.write_command(IridiumCommand.SIGNAL)
        if not success:
            self.state_field_registry.raise_flag(ErrorFlag.IRIDIUM_FAILURE)
