from MainControlLoop.lib.drivers.Iridium import Iridium, Commands
from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry, StateField, ErrorFlag
from time import sleep

class IridiumReadTask:
    CLEAR_BUFFER_TIMEOUT = 30

    def __init__(self, iridium: Iridium, state_field_registry: StateFieldRegistry):
        self.iridium: Iridium = iridium
        self.state_field_registry: StateFieldRegistry = state_field_registry
        self.buffer = []
        self.last_message = ""

    def execute(self):
        current_time: float = self.state_field_registry.get(StateField.TIME)
        self.buffer = []
        self.iridium.flush()

        # TODO: Find which command should the read task should execute
        command = Commands.CHECK_NETWORK.value
        if not self.iridium.write(command):
            self.state_field_registry.raise_flag(ErrorFlag.APRS_FAILURE)
            return

        sleep(.1)
        self.last_message = ""
        line =  self.iridium.readLine()
        while line:
            self.buffer.extend(line)
            line = self.iridium.readLine()
            if 'OK' in line:
                break

        if not self.buffer:
            # Iridium Hardware Fault
            self.state_field_registry.raise_flag(ErrorFlag.IRIDIUM_FAILURE)
            return
        
        message = ''.join(chr(b) for b in self.buffer)
        self.last_message = message
        self.state_field_registry.update(StateField.IRIDIUM_LAST_MESSAGE_TIME, current_time)