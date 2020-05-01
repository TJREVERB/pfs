from MainControlLoop.lib.pseudo_drivers import AntennaDeployer
from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry, StateField, ErrorFlag


class AntennaDeployerActuateTask:

    def __init__(self, antenna_deployer: AntennaDeployer, state_field_registry: StateFieldRegistry):
        self.antenna_deployer: AntennaDeployer = antenna_deployer
        self.state_field_registry: StateFieldRegistry = state_field_registry


    def disarm(self):
        success = self.antenna_deployer.disable()
        if not success:
            self.state_field_registry.raise_flag(ErrorFlag.ANTENNA_DEPLOYER_FAILURE)
            return

        self.state_field_registry.drop_flag(ErrorFlag.ANTENNA_DEPLOYER_FAILURE)


    def deploy(self):
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


    def execute(self):
        print("Antenna deployer actuatetask")
