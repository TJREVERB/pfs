from MainControlLoop.lib.drivers.APRS import APRS
from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry


class APRSCriticalMessageActuateTask:
    MAX_CRITICAL_MESSAGE_LEN = 100  # FIXME: find actual maximum

    def __init__(self, aprs: APRS, state_field_registry: StateFieldRegistry):
        self.aprs: APRS = aprs
        self.state_field_registry: StateFieldRegistry = state_field_registry
        self.run: bool = False
        self.critical_message: str = ""

    def set_beacon(self, critical_message: str):
        if not isinstance(critical_message, str):
            return
        if len(critical_message) > self.MAX_CRITICAL_MESSAGE_LEN:
            return
        self.critical_message = critical_message

    def execute(self):
        if not self.run:
            return

        if self.critical_message == "":
            self.run = False
            return

        self.aprs.write(self.critical_message)
        self.critical_message = ""
        self.run = False
