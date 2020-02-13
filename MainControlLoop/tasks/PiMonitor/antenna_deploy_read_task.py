from time import time as sys_time
from os import path

from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry, StateField


class AntennaDeployReadTask:

    def __init__(self, state_field_registry: StateFieldRegistry):
        self.state_field_registry: StateFieldRegistry = state_field_registry

    def execute(self):
        self.state_field_registry.update(StateField.ANTENNA_DEPLOY, path.exists("/root/antenna_deployed"))