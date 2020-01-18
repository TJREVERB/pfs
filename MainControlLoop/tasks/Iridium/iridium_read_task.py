from MainControlLoop.lib.drivers.Iridium import Iridium
from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry, StateField


class Iridium_ReadTask:

    def __init__(self, iridium: Iridium, state_field_registry: StateFieldRegistry):
        self.iridium: Iridium = iridium
        self.state_field_registry: StateFieldRegistry = state_field_registry
        self.buffer = []

    def execute(self):
        # TODO: Add a timeout to clear buffer
        next_byte = self.iridium.read()

        if next_byte is False:
            # Iridium Hardware Fault
            # TODO: Figure out how to represent hardware fault flags in the SFR
            return

        if len(next_byte) == 0:
            return

        if next_byte == '\n'.encode('utf-8'):
            message = ""
            while len(self.buffer) > 0:
                buffer_byte = self.buffer.pop(0)
                message += buffer_byte.decode('utf-8')
            # TODO: Figure out how to represent Iridium messages in the SFR
            return

        self.buffer.append(next_byte)
