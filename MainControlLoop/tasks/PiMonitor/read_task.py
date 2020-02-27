from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry

from .read import AntennaDeployReadTask, BootWaitCompleteReadTask, SystemTimeReadTask


class PiMonitorReadTask:

    def __init__(self, state_field_registry: StateFieldRegistry):
        self.sys_time_read_task = SystemTimeReadTask(state_field_registry)
        self.first_boot_read_task = BootWaitCompleteReadTask(state_field_registry)
        self.antenna_deploy_read_task = AntennaDeployReadTask(state_field_registry)

    def execute(self):
        self.sys_time_read_task.execute()
        self.first_boot_read_task.execute()
        self.antenna_deploy_read_task.execute()
