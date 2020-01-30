from MainControlLoop.lib.drivers.Iridium import Iridium
from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry, StateField


class IridiumReadTask:

    CLEAR_BUFFER_TIMEOUT = 30

    def __init__(self, iridium: Iridium, state_field_registry: StateFieldRegistry):
        self.iridium: Iridium = iridium
        self.state_field_registry: StateFieldRegistry = state_field_registry
        self.buffer = []
        self.last_message = ""

    def execute(self):

        current_time: float = self.state_field_registry.get(StateField.SYS_TIME)
        last_message_time: float = self.state_field_registry.get(StateField.IRIDIUM_LAST_MESSAGE_TIME)
        if current_time - last_message_time > self.CLEAR_BUFFER_TIMEOUT:
            self.buffer = []

        next_byte: bytes = self.iridium.read()
        self.last_message = ""

        if next_byte is False:
            # Iridium Hardware Fault
            # TODO: Figure out how to represent hardware fault flags in the SFR
            return

        if len(next_byte) == 0:
            return

        if next_byte == '\n'.encode('utf-8'):
            message: str = ""
            while len(self.buffer) > 0:
                buffer_byte: bytes = self.buffer.pop(0)
                message += buffer_byte.decode('utf-8')

            self.last_message = message
            self.state_field_registry.update(StateField.IRIDIUM_LAST_MESSAGE_TIME, current_time)
            return

        self.buffer.append(next_byte)
