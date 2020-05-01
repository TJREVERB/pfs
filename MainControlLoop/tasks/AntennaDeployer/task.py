from MainControlLoop.lib.pseudo_drivers.AntennaDeployer import AntennaDeployer
from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry
from MainControlLoop.lib.modes import Mode
from MainControlLoop.tasks.AntennaDeployer.read_task import AntennaDeployerReadTask
from MainControlLoop.tasks.AntennaDeployer.control_task import AntennaDeployerControlTask
from MainControlLoop.tasks.AntennaDeployer.actuate_task import AntennaDeployerActuateTask


class AntennaDeployerTask:

    def __init__(self, state_field_registry: StateFieldRegistry):
        self.antenna_deployer: AntennaDeployer = AntennaDeployer()
        self.state_field_registry: StateFieldRegistry = state_field_registry
        self.mode = Mode.BOOT

        self.read_task = AntennaDeployerReadTask(self.antenna_deployer, self.state_field_registry)
        self.control_task = AntennaDeployerControlTask(self.antenna_deployer, self.state_field_registry)
        self.actuate_task = AntennaDeployerActuateTask(self.antenna_deployer, self.state_field_registry)


    def set_mode(self, mode: Mode):
        if not isinstance(mode, Mode):
            return
        self.mode = mode


    def read(self):
        self.read_task.execute()


    def control(self):
        self.control_task.execute()


    def actuate(self):
        self.actuate_task.execute()
