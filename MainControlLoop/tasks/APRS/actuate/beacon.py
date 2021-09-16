# Sends message through APRS radio
# Set the message using set_beacon(beacon: str) instance method and then calling the instance execute() method

from MainControlLoop.lib.drivers.APRS import APRS
from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry, StateField, ErrorFlag


class APRSBeaconActuateTask:
    MAX_BEACON_LEN = 256

    def __init__(self, aprs: APRS, state_field_registry: StateFieldRegistry):
        self.aprs: APRS = aprs
        self.state_field_registry: StateFieldRegistry = state_field_registry
        self.run: bool = False
        self.beacon: str = ""

    def set_beacon(self, beacon: str):
        if not isinstance(beacon, str):
            return
        if len(beacon) > self.MAX_BEACON_LEN:
            return
        self.beacon = beacon

    def execute(self):
        if not self.run:
            return

        self.run = False
        if self.beacon == "":
            return

        success = self.aprs.write(self.beacon)
        self.beacon = ""

        if not success:
            self.state_field_registry.raise_flag(ErrorFlag.APRS_FAILURE)
            return

        self.state_field_registry.drop_flag(ErrorFlag.APRS_FAILURE)
        current_time = self.state_field_registry.get(StateField.TIME)
        self.state_field_registry.update(StateField.APRS_LAST_BEACON_TIME, current_time)
