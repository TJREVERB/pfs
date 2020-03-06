from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry
from MainControlLoop.tasks.PiMonitor.read_task import PiMonitorReadTask
from MainControlLoop.tasks.PiMonitor.actuate_task import PiMonitorActuateTask
from MainControlLoop.tasks.PiMonitor.control_task import PiMonitorControlTask


class PiMonitorTask:

    def __init__(self, state_field_registry: StateFieldRegistry):
        self.state_field_registry: StateFieldRegistry = state_field_registry
        self.read_task: PiMonitorReadTask = PiMonitorReadTask()
        self.actuate_task: PiMonitorActuateTask = PiMonitorActuateTask()
        self.control_task: PiMonitorControlTask = PiMonitorControlTask(state_field_registry, self.actuate_task)

    def read(self):
        self.read_task.execute()

    def control(self, commands):
        self.control_task.execute(commands)

    def actuate(self):
        self.actuate_task.execute()
