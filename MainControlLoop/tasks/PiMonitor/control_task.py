from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry, StateField

from MainControlLoop.tasks.PiMonitor.actuate_task import PiMonitorActuateTask


class PiMonitorControlTask:
    BOOT_INTERVAL = 1800

    def __init__(self, state_field_registry: StateFieldRegistry, actuate_task: PiMonitorActuateTask):
        self.state_field_registry: StateFieldRegistry = state_field_registry
        self.actuate_task: PiMonitorActuateTask = actuate_task

    def execute(self):
        current_time = self.state_field_registry.get(StateField.TIME)
        boot_time = self.state_field_registry.get(StateField.BOOT_TIME)

        if current_time - boot_time > self.BOOT_INTERVAL:
            self.actuate_task.enable_boot_complete()
