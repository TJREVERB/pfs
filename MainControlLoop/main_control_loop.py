from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry
from MainControlLoop.tasks.PiMonitor import PiMonitorTask
from MainControlLoop.tasks.APRS import APRSTask
from MainControlLoop.tasks.Iridium import IridiumTask
from MainControlLoop.tasks.core import Core


class MainControlLoop:

    def __init__(self):
        self.state_field_registry: StateFieldRegistry = StateFieldRegistry()
        self.pi_monitor: PiMonitorTask = PiMonitorTask(self.state_field_registry)
        self.APRS_task: APRSTask = APRSTask(self.state_field_registry)
        self.iridium_task: IridiumTask = IridiumTask(self.state_field_registry)
        self.core: Core = Core(self.state_field_registry, self.APRS_task)

    def execute(self):
        # READ BLOCK
        self.pi_monitor.read()
        APRS_message = self.APRS_task.read()
        iridium_message = self.iridium_task.read()

        # CONTROL BLOCK
        self.core.control([APRS_message, iridium_message])
        self.APRS_task.control([APRS_message, iridium_message])

        # ACTUATE BLOCK
        self.APRS_task.actuate()
