from time import time as sys_time
from os import path

from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry, StateField


class FirstBootReadTask:

    def __init__(self, state_field_registry: StateFieldRegistry):
        self.state_field_registry: StateFieldRegistry = state_field_registry

    def execute(self):
       if path.exists("/root/first_boot"):
          self.state_field_registry.FIRST_BOOT: bool = True
       else:
          self.state_field_registry.FIRST_BOOT: bool = False


