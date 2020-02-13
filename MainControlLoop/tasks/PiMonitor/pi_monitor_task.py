from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry
from MainControlLoop.tasks.PiMonitor.system_time_read_task import SystemTimeReadTask
from MainControlLoop.tasks.PiMonitor.first_boot_read_task import FirstBootReadTask
from MainControlLoop.tasks.PiMonitor.antenna_deploy_read_task import AntennaDeployReadTask

class PiMonitorTask:

    def __init__(self, state_field_registry: StateFieldRegistry):
        self.state_field_registry: StateFieldRegistry = state_field_registry
        self.sys_time_read_task = SystemTimeReadTask(self.state_field_registry)
        self.first_boot_read_task = FirstBootReadTask(self.state_field_registry)
        self.antenna_deploy_read_task = AntennaDeployReadTask(self.state_field_registry)

    def read(self):
        self.sys_time_read_task.execute()
        self.first_boot_read_task.execute()
        self.antenna_deploy_read_task.execute()
