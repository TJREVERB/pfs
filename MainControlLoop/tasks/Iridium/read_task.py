import re
from enum import Enum

from MainControlLoop.lib.drivers.Iridium import Iridium, IridiumCommand
from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry, StateField, ErrorFlag


class Response(Enum):
    OK = "OK"
    ERROR = "ERROR"


class IridiumReadTask:

    CLEAR_BUFFER_TIMEOUT = 30

    def __init__(self, iridium: Iridium, state_field_registry: StateFieldRegistry):
        self.iridium: Iridium = iridium
        self.state_field_registry: StateFieldRegistry = state_field_registry
        self.buffer = []
        self.last_message = ""

    def execute(self):
        self.last_message = ""

        current_time: float = self.state_field_registry.get(StateField.TIME)
        last_message_time: float = self.state_field_registry.get(StateField.IRIDIUM_LAST_MESSAGE_TIME)
        if current_time - last_message_time > self.CLEAR_BUFFER_TIMEOUT:
            self.buffer = []

        next_bytes, success = self.iridium.read()

        if success is False:
            # Iridium Hardware Fault
            self.state_field_registry.raise_flag(ErrorFlag.IRIDIUM_FAILURE)
            return

        self.state_field_registry.drop_flag(ErrorFlag.IRIDIUM_FAILURE)

        if len(next_bytes) == 0:
            return

        self.buffer.append(next_bytes)
        buffer_content = ''.join([b.decode('UTF-8') for b in self.buffer])
        buffer_items = re.split(r'OK|ERROR', buffer_content)
        self.buffer = []

        for item in buffer_items:
            if item == '' or item == '\r\n':
                continue

            if Response.OK.value not in item and Response.ERROR.value not in item:
                self.buffer.append(item.encode('UTF-8'))
                continue

            self.state_field_registry.update(StateField.IRIDIUM_LAST_MESSAGE_TIME, current_time)

            if IridiumCommand.GEOLOCATION.value in item:
                item_split = re.split(r'MSGEO:', item)
                if len(item_split) < 2:
                    continue

                location = re.split('\r', item_split[1].strip())[0]
                self.state_field_registry.update(StateField.GEOLOCATION, location)
                continue

            if IridiumCommand.SIGNAL.value in item:
                signal_strength = int('0' + re.sub(r'[^\d]*', '', item))
                self.state_field_registry.update(StateField.IRIDIUM_SIGNAL, signal_strength)
                continue

            self.last_message = item.replace('OK', '')
