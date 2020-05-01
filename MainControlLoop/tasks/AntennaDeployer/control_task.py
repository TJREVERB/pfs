from MainControlLoop.lib.pseudo_drivers import AntennaDeployer
from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry, StateField, ErrorFlag


class AntennaDeployerControlTask:

    def __init__(self, antenna_deployer: AntennaDeployer, state_field_registry: StateFieldRegistry):
        self.antenna_deployer: AntennaDeployer = antenna_deployer
        self.state_field_registry: StateFieldRegistry = state_field_registry


    def execute(self):
        print(self.state_field_registry.get(StateField.AD_TEMP))