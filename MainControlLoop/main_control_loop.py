from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry
from MainControlLoop.tasks.PiMonitor import PiMonitorTask
from MainControlLoop.tasks.APRS import APRSTask
from MainControlLoop.tasks.Iridium import IridiumTask


class MainControlLoop:

    def __init__(self):
        self.state_field_registry = StateFieldRegistry()
        self.pi_monitor = PiMonitorTask(self.state_field_registry)
        self.APRS_task = APRSTask(self.state_field_registry)
        self.iridium_task = IridiumTask(self.state_field_registry)

    def execute(self):
        self.pi_monitor.read()
        self.APRS_task.read()
        self.iridium_task.read()
