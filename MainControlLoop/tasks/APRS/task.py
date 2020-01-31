from MainControlLoop.lib.drivers.APRS import APRS
from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry
from MainControlLoop.tasks.APRS.read_task import APRSReadTask
from MainControlLoop.tasks.APRS.control_task import APRSControlTask
from MainControlLoop.tasks.APRS.beacon_actuate_task import APRSBeaconActuateTask
from MainControlLoop.tasks.APRS.dump_actuate_task import APRSDumpActuateTask
from MainControlLoop.tasks.APRS.crticial_message_actuate_task import APRSCriticalMessageActuateTask


class APRSTask:

    def __init__(self, state_field_registry: StateFieldRegistry):
        self.aprs: APRS = APRS()
        self.state_field_registry: StateFieldRegistry = state_field_registry

        self.read_task = APRSReadTask(self.aprs, self.state_field_registry)

        self.beacon_actuate_task = APRSBeaconActuateTask(self.aprs, self.state_field_registry)
        self.dump_actuate_task = APRSDumpActuateTask(self.aprs, self.state_field_registry)
        self.critical_message_actuate_task = APRSCriticalMessageActuateTask(self.aprs, self.state_field_registry)

        self.control_task = APRSControlTask(self.aprs, self.state_field_registry, self.beacon_actuate_task, self.dump_actuate_task, self.critical_message_actuate_task)

    def read(self):
        self.read_task.execute()
        return self.read_task.last_message

    def control(self, commands):
        self.control_task.execute(commands)

    def actuate(self):
        self.critical_message_actuate_task.execute()
        self.beacon_actuate_task.execute()
        self.dump_actuate_task.execute()
