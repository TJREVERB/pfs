import os

from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry, StateField


class BootWaitCompleteReadTask:
    FILE_PATH = os.path.join(os.environ["HOME"], 'first_boot')

    def __init__(self, state_field_registry: StateFieldRegistry):
        self.state_field_registry: StateFieldRegistry = state_field_registry

    def execute(self):
        """
        Checks if current boot is first boot
        :return: (None)
        """
        self.state_field_registry.update(StateField.BOOT_WAIT_COMPLETE, os.path.exists(self.FILE_PATH))
