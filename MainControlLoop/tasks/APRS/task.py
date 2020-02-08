from MainControlLoop.lib.drivers.APRS import APRS
from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry
from MainControlLoop.lib.modes import Mode

from MainControlLoop.tasks.APRS.read_task import APRSReadTask
from MainControlLoop.tasks.APRS.control_task import APRSControlTask
from MainControlLoop.tasks.APRS.actuate_task import APRSActuateTask


class APRSTask:

    def __init__(self, state_field_registry: StateFieldRegistry):
        self.aprs: APRS = APRS()
        self.state_field_registry: StateFieldRegistry = state_field_registry
        self.mode = Mode.BOOT

        self.read_task = APRSReadTask(self.aprs, self.state_field_registry)
        self.actuate_task = APRSActuateTask(self.aprs, self.state_field_registry)
        self.control_task = APRSControlTask(self.aprs, self.state_field_registry, self.mode, self.actuate_task)

    def set_mode(self, mode: Mode):
        if not isinstance(mode, Mode):
            return

        self.mode = mode
        self.control_task.mode = self.mode

    def read(self):
        self.read_task.execute()
        return self.read_task.last_message

    def control(self, commands):
        self.control_task.execute(commands)

    def actuate(self):
        self.actuate_task.execute()
