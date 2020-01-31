from MainControlLoop.lib.drivers.APRS import APRS
from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry, ErrorFlag, StateField


class APRSReadTask:
    CLEAR_BUFFER_TIMEOUT = 30

    def __init__(self, aprs: APRS, state_field_registry: StateFieldRegistry):
        self.aprs: APRS = aprs
        self.state_field_registry: StateFieldRegistry = state_field_registry
        self.buffer: list = []
        self.last_message: str = ""

    def execute(self):
        current_time: float = self.state_field_registry.get(StateField.SYS_TIME)
        last_message_time: float = self.state_field_registry.get(StateField.APRS_LAST_MESSAGE_TIME)
        if current_time - last_message_time > self.CLEAR_BUFFER_TIMEOUT:
            self.buffer = []

        next_byte: bytes = self.aprs.read()
        self.last_message = ""

        if next_byte is False:
            # APRS Hardware Fault
            self.state_field_registry.raise_flag(ErrorFlag.APRS_FAILURE)
            return

        self.state_field_registry.drop_flag(ErrorFlag.APRS_FAILURE)

        if len(next_byte) == 0:
            return

        if next_byte == '\n'.encode('utf-8'):
            message: str = ""
            while len(self.buffer) > 0:
                buffer_byte: bytes = self.buffer.pop(0)
                message += buffer_byte.decode('utf-8')

            self.last_message = message
            self.state_field_registry.update(StateField.APRS_LAST_MESSAGE_TIME, current_time)
            return

        self.buffer.append(next_byte)
