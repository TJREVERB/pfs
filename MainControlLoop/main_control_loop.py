from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry
from MainControlLoop.tasks.PiMonitor import PiMonitorTask
from MainControlLoop.tasks.APRS import APRSTask
from MainControlLoop.tasks.Iridium import IridiumTask
from MainControlLoop.tasks.core import Core


class MainControlLoop:

    def __init__(self):
        self.state_field_registry: StateFieldRegistry = StateFieldRegistry()
        self.pi_monitor: PiMonitorTask = PiMonitorTask(self.state_field_registry)
        self.aprs_task: APRSTask = APRSTask(self.state_field_registry)
        self.iridium_task: IridiumTask = IridiumTask(self.state_field_registry)
        self.core: Core = Core(self.state_field_registry, self.aprs_task)

    def execute(self):
        # READ BLOCK
        self.pi_monitor.read()
        aprs_message = self.aprs_task.read()
        iridium_message = self.iridium_task.read()

        # CONTROL BLOCK
        self.core.control([aprs_message, iridium_message])
        self.aprs_task.control([aprs_message, iridium_message])

        # ACTUATE BLOCK
        self.aprs_task.actuate()
