from MainControlLoop.lib.drivers.AntennaDeployer import AntennaDeployer
from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry
from MainControlLoop.lib.modes import Mode
from MainControlLoop.tasks.AntennaDeployer.read_task import AntennaDeployerReadTask
from MainControlLoop.tasks.AntennaDeployer.deploy_task import AntennaDeployerDeployTask


class AntennaDeployerTask:

    def __init__(self, state_field_registry: StateFieldRegistry):
        self.antenna_deployer: AntennaDeployer = AntennaDeployer()
        self.state_field_registry: StateFieldRegistry = state_field_registry
        self.mode = Mode.BOOT

        self.read_task = AntennaDeployerReadTask(self.antenna_deployer, self.state_field_registry)
        self.deploy_task = AntennaDeployerDeployTask(self.antenna_deployer, self.state_field_registry)

    def set_mode(self, mode: Mode):
        if not isinstance(mode, Mode):
            return
        self.mode = mode

    def read(self):
        self.read_task.execute()
        return self.read_task.last_message

    def actuate(self):
        self.deploy_task.execute()
