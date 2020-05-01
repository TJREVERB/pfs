import time
from MainControlLoop.lib.pseudo_drivers import AntennaDeployer
from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry, StateField, ErrorFlag


class AntennaDeployerControlTask:

    def __init__(self, antenna_deployer: AntennaDeployer, state_field_registry: StateFieldRegistry):
        self.antenna_deployer: AntennaDeployer = antenna_deployer
        self.state_field_registry: StateFieldRegistry = state_field_registry
        self.time = time.time()
        self.last_deploy_time = time.time()


    def execute(self):
        deployed = self.state_field_registry.get(StateField.ANTENNA_DEPLOYED)
        # Basically after 5 seconds have passed, keep requesting to deploy antenna every .5s until it gets deployed
        if time.time() - self.time > 5 and not deployed and time.time() - self.last_deploy_time > 0.5:
            self.state_field_registry.update(StateField.DEPLOY_ANTENNA, True)
            self.last_deploy_time = time.time()
        if self.state_field_registry.get(StateField.AD_COUNTS) != [0, 0, 0, 0]:
            print(self.state_field_registry.get(StateField.AD_COUNTS))