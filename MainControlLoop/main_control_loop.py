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
        self.aprs: APRSTask = APRSTask(self.state_field_registry, self.locker)
        self.iridium: IridiumTask = IridiumTask(self.state_field_registry)
        self.core: Core = Core(self.state_field_registry, self.aprs)

    def execute(self):
        # READ BLOCK
        commands = ['', '', '']  # APRS, Iridium, System
        self.pi_monitor.read()
        commands[0] = self.aprs.read()
        commands[1] = self.iridium.read()

        # CONTROL BLOCK
        self.core.control(commands)
        self.archiver.control()
        self.pi_monitor.control(commands)
        self.aprs.control(commands)

        # ACTUATE BLOCK
        self.pi_monitor.actuate()
        self.aprs.actuate()

    def run(self):
        while True:
            self.execute()