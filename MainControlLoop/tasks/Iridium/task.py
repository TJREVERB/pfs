from MainControlLoop.lib.drivers.Iridium import Iridium
from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry
from MainControlLoop.lib.modes import Mode

from MainControlLoop.tasks.Iridium.read_task import IridiumReadTask
from MainControlLoop.tasks.Iridium.control_task import IridiumControlTask
from MainControlLoop.tasks.Iridium.actuate_task import IridiumActuateTask


class IridiumTask:

    def __init__(self, state_field_registry: StateFieldRegistry):
        self.iridium: Iridium = Iridium()
        self.state_field_registry: StateFieldRegistry = state_field_registry
        self.mode = Mode.BOOT

        self.read_task = IridiumReadTask(self.iridium, self.state_field_registry)
        self.actuate_task = IridiumActuateTask(self.iridium, self.state_field_registry)
        self.control_task = IridiumControlTask(self.iridium, self.state_field_registry, self.actuate_task)

    def set_mode(self, mode: Mode):
        if not isinstance(mode, Mode):
            return

        self.mode = mode
        self.control_task.mode = self.mode

    def read(self):
        self.read_task.execute()
        return self.read_task.last_message

    def control(self):
        self.control_task.execute()

    def actuate(self):
        self.actuate_task.execute()
