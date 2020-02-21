from MainControlLoop.tasks.PiMonitor.actuate import BootCompleteActuateTask


class PiMonitorActuateTask:

    def __init__(self):
        self.boot_complete_actuate_task = BootCompleteActuateTask()

    def enable_boot_complete(self):
        self.boot_complete_actuate_task.run = True

    def execute(self):
        self.boot_complete_actuate_task.execute()
