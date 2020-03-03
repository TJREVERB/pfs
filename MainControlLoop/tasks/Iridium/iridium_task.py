# NOTE: All unimplemented code has been commented out and replaced with placeholders

from MainControlLoop.lib.drivers.Iridium import Iridium
from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry
from MainControlLoop.lib.modes import Mode
from MainControlLoop.tasks.Iridium.iridium_read_task import IridiumReadTask
from MainControlLoop.tasks.Iridium.iridium_control_task import IridiumControlTask

# TODO: Implement beacon_actuate_task, dump_actuate_task, and critical_message_actuate_task for Iridium
# from MainControlLoop.tasks.Iridium.iridium_beacon_actuate_task import IridiumBeaconActuateTask
# from MainControlLoop.tasks.Iridium.iridium_dump_actuate_task import IridiumDumpActuateTask
# from MainControlLoop.tasks.Iridium.iridium_crticial_message_actuate_task import IridiumCriticalMessageActuateTask


class IridiumTask:

    def __init__(self, state_field_registry: StateFieldRegistry):
        self.iridium: Iridium = Iridium()
        self.state_field_registry: StateFieldRegistry = state_field_registry
        self.mode = Mode.BOOT

        self.read_task = IridiumReadTask(self.iridium, self.state_field_registry)

        # self.beacon_actuate_task = IridiumBeaconActuateTask(self.iridium, self.state_field_registry)
        # self.dump_actuate_task = IridiumDumpActuateTask(self.iridium, self.state_field_registry)
        # self.critical_message_actuate_task = IridiumCriticalMessageActuateTask(self.aprs, self.state_field_registry)

        self.control_task = IridiumControlTask(self.iridium, self.state_field_registry, self.mode, None,
                                            None, None)                                
        # self.control_task = IridiumControlTask(self.iridium, self.state_field_registry, self.mode, self.beacon_actuate_task,
        #                                     self.dump_actuate_task, self.critical_message_actuate_task)    
    def set_mode(self, mode: Mode):
        if not isinstance(mode, Mode):
            return
        self.mode = mode
        # self.control_task.mode = self.mode

    def read(self):
        self.read_task.execute()
        return self.read_task.last_message

    def control(self, commands):
        pass
        # self.control_task.execute(commands)

    def actuate(self):
        pass
        # self.critical_message_actuate_task.execute()
        # self.beacon_actuate_task.execute()
        # self.dump_actuate_task.execute()
