from MainControlLoop.lib.drivers.APRS import APRS
from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry


class APRSBeaconActuateTask:
    MAX_BEACON_LEN = 100  # FIXME: find actual maximum

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

        if self.beacon == "":
            self.run = False
            return

        self.aprs.write(self.beacon)
        self.beacon = ""
        self.run = False
