from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry, StateField
from MainControlLoop.tasks.APRS import APRS_Task
from MainControlLoop.tasks.Iridium import IridiumTask


class MainControlLoop:

    def __init__(self):
        self.state_field_registry = StateFieldRegistry()
        self.APRS_task = APRS_Task(self.state_field_registry)
        self.iridium_task = IridiumTask(self.state_field_registry)

    def execute(self):
        self.APRS_task.read()
        self.iridium_task.read()
