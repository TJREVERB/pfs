from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry, StateFieldRegistryLocker
from MainControlLoop.tasks.PiMonitor import PiMonitorTask
from MainControlLoop.tasks.StateFieldRegistryArchiver import StateFieldRegistryArchiver
from MainControlLoop.tasks.APRS import APRSTask
from MainControlLoop.tasks.Iridium import IridiumTask
from MainControlLoop.tasks.core import Core


class MainControlLoop:

    def __init__(self):
        self.state_field_registry: StateFieldRegistry = StateFieldRegistry()
        self.locker: StateFieldRegistryLocker = StateFieldRegistryLocker()
        self.pi_monitor: PiMonitorTask = PiMonitorTask(self.state_field_registry)
        self.archiver: StateFieldRegistryArchiver = StateFieldRegistryArchiver(self.state_field_registry, self.locker)
        self.aprs_task: APRSTask = APRSTask(self.state_field_registry, self.locker)
        self.iridium_task: IridiumTask = IridiumTask(self.state_field_registry)
        self.core: Core = Core(self.state_field_registry, self.aprs_task)

    def execute(self):
        # READ BLOCK
        commands = []
        self.pi_monitor.read()
        commands.append(self.aprs_task.read())
        commands.append(self.iridium_task.read())

        # CONTROL BLOCK
        self.core.control(commands)
        self.archiver.control()
        self.aprs_task.control(commands)

        # ACTUATE BLOCK
        self.aprs_task.actuate()
