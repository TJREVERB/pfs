from MainControlLoop.tasks.PiMonitor.actuate import BootCompleteActuateTask, AntennaDeployedActuateTask


class PiMonitorActuateTask:

    def __init__(self):
        self.boot_complete_actuate_task = BootCompleteActuateTask()
        self.antenna_deployed_actuate_task = AntennaDeployedActuateTask()

    def enable_boot_complete(self):
        self.boot_complete_actuate_task.run = True

    def enable_antenna_deployed(self):
        self.antenna_deployed_actuate_task.run = True

    def execute(self):
        self.boot_complete_actuate_task.execute()
        self.antenna_deployed_actuate_task.execute()
