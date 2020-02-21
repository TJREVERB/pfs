from os import path

from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry, StateField


class BootWaitCompleteReadTask:

    def __init__(self, state_field_registry: StateFieldRegistry):
        self.state_field_registry: StateFieldRegistry = state_field_registry

    def execute(self):
        """
        Checks if current boot is first boot
        :return: (None)
        """
        self.state_field_registry.update(StateField.BOOT_WAIT_COMPLETE, path.exists("/root/first_boot"))


