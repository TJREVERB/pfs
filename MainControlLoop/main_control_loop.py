from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry, StateFieldRegistryLocker
from MainControlLoop.tasks.PiMonitor import PiMonitorTask
from MainControlLoop.tasks.StateFieldRegistryArchiver import StateFieldRegistryArchiver
from MainControlLoop.tasks.APRS import APRSTask
from MainControlLoop.tasks.Iridium import IridiumTask
from MainControlLoop.tasks.core import Core

# MainControlLoop runs read, control, and actuate repeatedly

class MainControlLoop:

    def __init__(self):
        self.state_field_registry: StateFieldRegistry = StateFieldRegistry()  # sets up the state field registry to store global variables
        self.locker: StateFieldRegistryLocker = StateFieldRegistryLocker() # kind of like an archive of the statefields
        self.pi_monitor: PiMonitorTask = PiMonitorTask(self.state_field_registry)
        self.archiver: StateFieldRegistryArchiver = StateFieldRegistryArchiver(self.state_field_registry, self.locker)
        self.aprs: APRSTask = APRSTask(self.state_field_registry, self.locker)
        self.iridium: IridiumTask = IridiumTask(self.state_field_registry)
        self.core: Core = Core(self.state_field_registry, self.aprs)

    def execute(self):
        # READ BLOCK
        commands = ['', '', '']  # APRS, Iridium, System
        self.pi_monitor.read()  # updates time, checks if it is the first time it has booted and if antenna is deployed
        
        # reads last message from aprs and iridium and updates statefield
        commands[0] = self.aprs.read()  
        commands[1] = self.iridium.read()

        # CONTROL BLOCK
        self.core.control(commands) # checks mode and executes commands based on mode
        self.archiver.control() # stores the statefieldregistry in the statefieldlocker
        self.pi_monitor.control(commands)  # determines if pi can release antenna
        self.aprs.control(commands)

        # ACTUATE BLOCK
        self.pi_monitor.actuate()
        self.aprs.actuate()  # sends messages back down to gs

    def run(self):
        while True:
            self.execute()