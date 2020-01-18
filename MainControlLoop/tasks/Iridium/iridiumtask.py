from MainControlLoop.lib.drivers.Iridium import Iridium
from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry
from MainControlLoop.tasks.Iridium.iridium_read_task import Iridium_ReadTask


class IridiumTask:

    def __init__(self, state_field_registry: StateFieldRegistry):
        self.iridium: Iridium = Iridium()
        self.state_field_registry: StateFieldRegistry = state_field_registry
        self.read_task = Iridium_ReadTask(self.iridium, self.state_field_registry)

    def read(self):
        self.read_task.execute()
