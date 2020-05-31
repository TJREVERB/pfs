from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry, StateField, StateFieldRegistryLocker


class StateFieldRegistryArchiver:
    ARCHIVE_INTERVAL = 30

    def __init__(self, state_field_registry: StateFieldRegistry, locker: StateFieldRegistryLocker):
        self.state_field_registry: StateFieldRegistry = state_field_registry
        self.locker: StateFieldRegistryLocker = locker

    def control(self):
        last_archive_time: float = self.state_field_registry.get(StateField.LAST_ARCHIVE_TIME)
        current_sys_time: float = self.state_field_registry.get(StateField.TIME)

        if current_sys_time - last_archive_time > self.ARCHIVE_INTERVAL:
            self.locker.store(self.state_field_registry)
