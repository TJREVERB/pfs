from MainControlLoop.lib.drivers.APRS import APRS
from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry
from MainControlLoop.tasks.APRS.APRS_read_task import APRS_ReadTask


class APRS_Task:

    def __init__(self, state_field_registry: StateFieldRegistry):
        self.aprs: APRS = APRS()
        self.state_field_registry: StateFieldRegistry = state_field_registry
        self.read_task = APRS_ReadTask(self.aprs, self.state_field_registry)

    def read(self):
        self.read_task.execute()
