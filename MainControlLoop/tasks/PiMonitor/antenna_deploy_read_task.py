from time import time as sys_time
from os import path

from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry, StateField


class AntennaDeployReadTask:

    def __init__(self, state_field_registry: StateFieldRegistry):
        self.state_field_registry: StateFieldRegistry = state_field_registry

    def execute(self):
       if path.exists("/root/antenna_deployed"):
          self.state_field_registry.ANTENNA_DEPLOY: bool = True
       else:
          self.state_field_registry.ANTENNA_DEPLOY: bool = False


