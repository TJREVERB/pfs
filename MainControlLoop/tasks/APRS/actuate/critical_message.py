# This file is used to send critical messages to the groundstation
# it can send any message listed in the APRSCriticalMessage class
# To use it, call the instance method set_message(APRSCriticalMessage) with an APRSCriticalMessage object whose .value field is the critical message which you wish to send, then call the .execute() instance method

from MainControlLoop.lib.drivers.APRS import APRS
from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry, ErrorFlag

from enum import Enum


class APRSCriticalMessage(Enum):
    ANTS_DEPLOYED = "TJ:CRIT;ANTS_DEPLOYED;"
    ENTERED_COMMS = "TJ:CRIT;ENTERED_COMMS;"


class APRSCriticalMessageActuateTask:
    def __init__(self, aprs: APRS, state_field_registry: StateFieldRegistry):
        self.aprs: APRS = aprs
        self.state_field_registry: StateFieldRegistry = state_field_registry
        self.run: bool = False
        self.message: str = ""

    def set_message(self, critical_message: APRSCriticalMessage):
        if not isinstance(critical_message, APRSCriticalMessage):
            return

        self.message = critical_message.value

    def execute(self):
        if not self.run:
            return

        self.run = False
        if self.message == "":
            return

        success = self.aprs.write(self.message)
        self.message = ""

        if not success:
            self.state_field_registry.raise_flag(ErrorFlag.APRS_FAILURE)
            return

        self.state_field_registry.drop_flag(ErrorFlag.APRS_FAILURE)

