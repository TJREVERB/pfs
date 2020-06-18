import os

from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry, StateField


class AntennaDeployReadTask:
    FILE_PATH = os.path.join(os.environ["HOME"], 'antenna_deployed')

    def __init__(self, state_field_registry: StateFieldRegistry):
        self.state_field_registry: StateFieldRegistry = state_field_registry

    def execute(self):
        """
        Checks if antenna has been deployed
        :return: (None)
        """

        self.state_field_registry.update(StateField.ANTENNA_DEPLOYED, os.path.exists(self.FILE_PATH))
