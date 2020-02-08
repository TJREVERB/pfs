from MainControlLoop.lib.drivers import APRS
from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry

from .beacon_actuate_task import APRSBeaconActuateTask
from .dump_actuate_task import APRSDumpActuateTask
from .crticial_message_actuate_task import APRSCriticalMessageActuateTask


class APRSActuateTask:

    def __init__(self, aprs: APRS, state_field_registry: StateFieldRegistry):
        self.beacon_actuate_task = APRSBeaconActuateTask(aprs, state_field_registry)
        self.dump_actuate_task = APRSDumpActuateTask(aprs, state_field_registry)
        self.critical_message_actuate_task = APRSCriticalMessageActuateTask(aprs, state_field_registry)

    def set_dump(self, dump):
        self.dump_actuate_task.set_dump(dump)

    def set_beacon(self, beacon):
        self.beacon_actuate_task.set_beacon(beacon)

    def enable_beacon(self):
        self.beacon_actuate_task.run = True

    def enable_dump(self):
        self.dump_actuate_task.run = True

    def enable_critical_message(self):
        self.critical_message_actuate_task.run = True

    def execute(self):
        self.critical_message_actuate_task.execute()
        self.beacon_actuate_task.execute()
        self.dump_actuate_task.execute()
