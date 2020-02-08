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

        current_time: float = self.state_field_registry.get(StateField.TIME)
        last_message_time: float = self.state_field_registry.get(StateField.IRIDIUM_LAST_MESSAGE_TIME)
        if current_time - last_message_time > self.CLEAR_BUFFER_TIMEOUT:
            self.buffer = []

        resp, success = self.iridium.write(self.iridium.BATTERY_CHECK)
        if not (success and resp):
            # TODO: Represent serial communication failures in SFR
            return
        
        for field in StateField.IRIDIUM_BCS, StateField.IRIDIUM_BCL:
            self.last_message = ""
            next_byte: bytes = self.iridium.read()            
            if next_byte is False:
                # Iridium Hardware Fault
                # TODO: Figure out how to represent hardware fault flags in the SFR
                return

            self.last_message = str(next_byte) # TODO: Map a status code to a proper message string
            self.buffer.append(next_byte)            
            self.state_field_registry.update(field, int(next_byte)) # TODO: Ensure next_byte is a valid status code