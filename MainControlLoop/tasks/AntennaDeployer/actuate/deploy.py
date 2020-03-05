from MainControlLoop.lib.drivers import AntennaDeployer
from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry, StateField, ErrorFlag


class AntennaDeployActuateTask:

    def __init__(self, antenna_deployer: AntennaDeployer, state_field_registry: StateFieldRegistry):
        self.antenna_deployer: AntennaDeployer = antenna_deployer
        self.state_field_registry: StateFieldRegistry = state_field_registry
        self.run: bool = False

    def execute(self):
        if not self.run:
            return

        self.run = False
        success = self.antenna_deployer.enable()
        if not success:
            self.state_field_registry.raise_flag(ErrorFlag.ANTENNA_DEPLOYER_FAILURE)
            return

        success = self.antenna_deployer.write(AntennaDeployer.AntennaDeployerCommand.DEPLOY_1, 0x0A)
        success &= self.antenna_deployer.write(AntennaDeployer.AntennaDeployerCommand.DEPLOY_2, 0x0A)
        success &= self.antenna_deployer.write(AntennaDeployer.AntennaDeployerCommand.DEPLOY_3, 0x0A)
        success &= self.antenna_deployer.write(AntennaDeployer.AntennaDeployerCommand.DEPLOY_4, 0x0A)

        if not success:
            self.state_field_registry.raise_flag(ErrorFlag.ANTENNA_DEPLOYER_FAILURE)
            return

        self.state_field_registry.drop_flag(ErrorFlag.ANTENNA_DEPLOYER_FAILURE)
        self.state_field_registry.update(StateField.ANTENNA_DEPLOY_ATTEMPTED, True)
