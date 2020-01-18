from MainControlLoop.lib.drivers.APRS import APRS
from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry, StateField


class APRS_ReadTask:

    def __init__(self, aprs: APRS, state_field_registry: StateFieldRegistry):
        self.aprs: APRS = aprs
        self.state_field_registry: StateFieldRegistry = state_field_registry
        self.buffer = []

    def execute(self):
        # TODO: Add a timeout to clear buffer
        next_byte = self.aprs.read()

        if next_byte is False:
            # APRS Hardware Fault
            # TODO: Figure out how to represent hardware fault flags in the SFR
            return

        if len(next_byte) == 0:
            return

        if next_byte == '\n'.encode('utf-8'):
            message = ""
            while len(self.buffer) > 0:
                buffer_byte = self.buffer.pop(0)
                message += buffer_byte.decode('utf-8')
            # TODO: Figure out how to represent APRS messages in the SFR
            return

        self.buffer.append(next_byte)
