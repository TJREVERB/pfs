from MainControlLoop.lib.pseudo_drivers.AntennaDeployer import AntennaDeployer, AntennaDeployerWriteCommand
from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry, StateField, ErrorFlag


class AntennaDeployerActuateTask:

    def __init__(self, antenna_deployer: AntennaDeployer, state_field_registry: StateFieldRegistry):
        self.antenna_deployer: AntennaDeployer = antenna_deployer
        self.state_field_registry: StateFieldRegistry = state_field_registry


    def disarm(self):
        success = self.antenna_deployer.write(AntennaDeployerWriteCommand.DISARM_ANTS)
        if not success:
            self.state_field_registry.raise_flag(ErrorFlag.ANTENNA_DEPLOYER_FAILURE)
            return

        self.state_field_registry.drop_flag(ErrorFlag.ANTENNA_DEPLOYER_FAILURE)


    def deploy(self):
        success = self.antenna_deployer.write(AntennaDeployerWriteCommand.ARM_ANTS)
        if not success:
            self.state_field_registry.raise_flag(ErrorFlag.ANTENNA_DEPLOYER_FAILURE)
            return

        success = self.antenna_deployer.write(AntennaDeployerWriteCommand.DEPLOY_1)
        success &= self.antenna_deployer.write(AntennaDeployerWriteCommand.DEPLOY_2)
        success &= self.antenna_deployer.write(AntennaDeployerWriteCommand.DEPLOY_3)
        success &= self.antenna_deployer.write(AntennaDeployerWriteCommand.DEPLOY_4)

        self.state_field_registry.update(StateField.ANTENNA_DEPLOY_ATTEMPTED, True)
        if not success:
            self.state_field_registry.raise_flag(ErrorFlag.ANTENNA_DEPLOYER_FAILURE)
            return

        self.state_field_registry.drop_flag(ErrorFlag.ANTENNA_DEPLOYER_FAILURE)
        self.state_field_registry.update(StateField.ANTENNA_DEPLOY_ATTEMPTED, True)


    def execute(self):
        need_to_deploy = self.state_field_registry.get(StateField.DEPLOY_ANTENNA)
        if need_to_deploy:
            self.deploy()
            self.state_field_registry.update(StateField.DEPLOY_ANTENNA, False)
