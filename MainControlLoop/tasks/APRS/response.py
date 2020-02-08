from MainControlLoop.lib.drivers.APRS import APRS
from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry, StateField


class APRSResponseActuateTask:
    MAX_RESPONSE_LEN = 100  # FIXME: find actual maximum

    def __init__(self, aprs: APRS, state_field_registry: StateFieldRegistry):
        self.aprs: APRS = aprs
        self.state_field_registry: StateFieldRegistry = state_field_registry
        self.run: bool = False
        self.response: str = ""

    def set_response(self, response: str):
        if not isinstance(response, str):
            return
        if len(response) > self.MAX_RESPONSE_LEN:
            return
        self.response = response

    def execute(self):
        if not self.run:
            return

        self.run = False
        if self.response == "":
            return

        self.aprs.write(self.response)
        self.response = ""
