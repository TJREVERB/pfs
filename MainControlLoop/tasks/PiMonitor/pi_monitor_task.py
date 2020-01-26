from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry
from MainControlLoop.tasks.PiMonitor.system_time_read_task import SystemTimeReadTask


class PiMonitorTask:

    def __init__(self, state_field_registry: StateFieldRegistry):
        self.state_field_registry: StateFieldRegistry = state_field_registry
        self.sys_time_read_task = SystemTimeReadTask(self.state_field_registry)

    def read(self):
        self.sys_time_read_task.execute()
