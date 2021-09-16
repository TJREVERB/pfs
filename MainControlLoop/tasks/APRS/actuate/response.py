# This file is responsible for writing to the APRS radio
# this is done by setting the response message via the set_response(response: str) instance method and then calling the execute() instance method

from MainControlLoop.lib.drivers.APRS import APRS
from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry, ErrorFlag


class APRSResponseActuateTask:
    MAX_RESPONSE_LEN = 256

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

        success = self.aprs.write(self.response)
        self.response = ""

        if not success:
            self.state_field_registry.raise_flag(ErrorFlag.APRS_FAILURE)
            return

        self.state_field_registry.drop_flag(ErrorFlag.APRS_FAILURE)
