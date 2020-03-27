from MainControlLoop.lib.drivers import Iridium
from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry

from MainControlLoop.tasks.Iridium.actuate import IridiumDumpActuateTask
from MainControlLoop.tasks.Iridium.actuate import IridiumGeolocationActuateTask
from MainControlLoop.tasks.Iridium.actuate import IridiumResetActuateTask
from MainControlLoop.tasks.Iridium.actuate import IridiumSignalStrengthActuateTask


class IridiumActuateTask:

    def __init__(self, iridium: Iridium, state_field_registry: StateFieldRegistry):
        self.dump_actuate_task = IridiumDumpActuateTask(iridium, state_field_registry)
        self.geolocation_actuate_task = IridiumGeolocationActuateTask(iridium, state_field_registry)
        self.reset_actuate_task = IridiumResetActuateTask(iridium, state_field_registry)
        self.signal_strength_actuate_task = IridiumSignalStrengthActuateTask(iridium, state_field_registry)

    def set_dump(self, dump):
        self.dump_actuate_task.set_dump(dump)

    def enable_dump(self):
        self.dump_actuate_task.run = True

    def enable_geolocation(self):
        self.geolocation_actuate_task.run = True

    def enable_reset(self):
        self.reset_actuate_task.run = True

    def enable_signal_strength(self):
        self.signal_strength_actuate_task.run = True

    def execute(self):
        self.reset_actuate_task.execute()
        self.dump_actuate_task.execute()
        self.geolocation_actuate_task.execute()
        self.signal_strength_actuate_task.execute()
