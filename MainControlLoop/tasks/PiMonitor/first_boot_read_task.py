from time import time as sys_time
from os import path

from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry, StateField


class FirstBootReadTask:

    def __init__(self, state_field_registry: StateFieldRegistry):
        self.state_field_registry: StateFieldRegistry = state_field_registry

    def execute(self):
        self.state_field_registry.update(StateField.FIRST_BOOT, path.exists("/root/first_boot"))


