from MainControlLoop.lib.drivers import AntennaDeployer
from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry

from MainControlLoop.tasks.AntennaDeployer.actuate import AntennaDeployActuateTask
from MainControlLoop.tasks.AntennaDeployer.actuate import AntennaDisarmActuateTask


class AntennaDeployerActuateTask:

    def __init__(self, antenna_deployer: AntennaDeployer, state_field_registry: StateFieldRegistry):
        self.deploy_actuate_task = AntennaDeployActuateTask(antenna_deployer, state_field_registry)
        self.disarm_actuate_task = AntennaDisarmActuateTask(antenna_deployer, state_field_registry)

    def enable_deploy(self):
        self.deploy_actuate_task.run = True

    def enable_disarm(self):
        self.disarm_actuate_task.run = True
