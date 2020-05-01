from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry, StateFieldRegistryLocker
from MainControlLoop.tasks.PiMonitor import PiMonitorTask
from MainControlLoop.tasks.StateFieldRegistryArchiver import StateFieldRegistryArchiver
from MainControlLoop.tasks.AntennaDeployer.task import AntennaDeployerTask


class MainControlLoop:

    def __init__(self):
        self.state_field_registry: StateFieldRegistry = StateFieldRegistry()
        self.locker: StateFieldRegistryLocker = StateFieldRegistryLocker()
        self.archiver: StateFieldRegistryArchiver = StateFieldRegistryArchiver(self.state_field_registry, self.locker)
        self.antenna_deployer: AntennaDeployerTask = AntennaDeployerTask(self.state_field_registry)

    def execute(self):
        # READ BLOCK
        commands = ['', '', '']  # APRS, Iridium, System
        self.antenna_deployer.read()

        # CONTROL BLOCK
        self.antenna_deployer.control()

        # ACTUATE BLOCK
        self.antenna_deployer.actuate()


    def run(self):
        while True:
            self.execute()