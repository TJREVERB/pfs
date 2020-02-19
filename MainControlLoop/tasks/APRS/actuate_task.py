from MainControlLoop.lib.drivers import APRS
from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry

from MainControlLoop.tasks.APRS.actuate import APRSBeaconActuateTask
from MainControlLoop.tasks.APRS.actuate import APRSDumpActuateTask
from MainControlLoop.tasks.APRS.actuate import APRSCriticalMessageActuateTask, APRSCriticalMessage
from MainControlLoop.tasks.APRS.actuate import APRSResponseActuateTask
from MainControlLoop.tasks.APRS.actuate import APRSResetActuateTask


class APRSActuateTask:

    def __init__(self, aprs: APRS, state_field_registry: StateFieldRegistry):
        self.beacon_actuate_task = APRSBeaconActuateTask(aprs, state_field_registry)
        self.dump_actuate_task = APRSDumpActuateTask(aprs, state_field_registry)
        self.critical_message_actuate_task = APRSCriticalMessageActuateTask(aprs, state_field_registry)
        self.response_actuate_task = APRSResponseActuateTask(aprs, state_field_registry)
        self.reset_actuate_task = APRSResetActuateTask(aprs, state_field_registry)

    def set_dump(self, dump):
        self.dump_actuate_task.set_dump(dump)

    def set_beacon(self, beacon):
        self.beacon_actuate_task.set_beacon(beacon)

    def set_critical_message(self, critical_message: APRSCriticalMessage):
        self.critical_message_actuate_task.set_message(critical_message)

    def set_response(self, response):
        self.response_actuate_task.set_response(response)

    def enable_beacon(self):
        self.beacon_actuate_task.run = True

    def enable_dump(self):
        self.dump_actuate_task.run = True

    def enable_critical_message(self):
        self.critical_message_actuate_task.run = True

    def enable_response(self):
        self.response_actuate_task.run = True

    def enable_reset(self):
        self.reset_actuate_task.run = True

    def execute(self):
        self.reset_actuate_task.execute()
        self.critical_message_actuate_task.execute()
        self.beacon_actuate_task.execute()
        self.response_actuate_task.execute()
        self.dump_actuate_task.execute()
