from MainControlLoop.lib.drivers.Iridium import Iridium
from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry
from MainControlLoop.tasks.Iridium.read_task import IridiumReadTask


class IridiumTask:

    def __init__(self, state_field_registry: StateFieldRegistry):
        self.iridium: Iridium = Iridium()
        self.state_field_registry: StateFieldRegistry = state_field_registry
        self.read_task = IridiumReadTask(self.iridium, self.state_field_registry)

    def read(self):
        self.read_task.execute()
        return self.read_task.last_message
