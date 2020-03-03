# NOTE: All unimplemented code has been commented out and replaced with placeholders

from MainControlLoop.lib.drivers.Iridium import Iridium
from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry, StateField
from MainControlLoop.lib.modes import Mode

# TODO: Implement beacon_actuate_task, dump_actuate_task, and critical_message_actuate_task for Iridium
# from MainControlLoop.tasks.Iridium.beacon_actuate_task import IridiumBeaconActuateTask
# from MainControlLoop.tasks.Iridium.dump_actuate_task import IridiumDumpActuateTask
# from MainControlLoop.tasks.Iridium.crticial_message_actuate_task import IridiumCriticalMessageActuateTask

from enum import Enum


class BeaconInterval(Enum):
    FAST = "FAST"
    SLOW = "SLOW"
    CUSTOM = "CUSTOM"
    NEVER = "OFF"


class IridiumControlTask:
    # def __init__(self, iridium: Iridium, state_field_registry: StateFieldRegistry, mode: Mode, beacon_actuate_task: APRSBeaconActuateTask, dump_actuate_task: APRSDumpActuateTask, critical_message_actuate_task: APRSCriticalMessageActuateTask):
    def __init__(self, iridium: Iridium, state_field_registry: StateFieldRegistry, mode: Mode, beacon_actuate_task, dump_actuate_task, critical_message_actuate_task):
        self.iridium: Iridium = iridium
        self.state_field_registry: StateFieldRegistry = state_field_registry

        self.beacon_interval_lookup: dict = {
            BeaconInterval.FAST: 30,
            BeaconInterval.SLOW: 120,
            BeaconInterval.CUSTOM: -1,
            BeaconInterval.NEVER: -1,
        }
        self.beacon_interval: BeaconInterval = BeaconInterval.NEVER
        self.mode: Mode = mode

        # self.beacon_actuate_task: APRSBeaconActuateTask = beacon_actuate_task
        # self.dump_actuate_task: APRSDumpActuateTask = dump_actuate_task
        # self.critical_message_actuate_task: APRSCriticalMessageActuateTask = critical_message_actuate_task

    def execute(self, commands):
        # TODO: control task logic HAS NOT been written for boot/startup
        # TODO: control logic HAS NOT been written for parsing commands

        if self.mode == Mode.SAFE:
            self.beacon_interval = BeaconInterval.NEVER
            # TODO: create a reset actuate task
            return

        if self.mode == Mode.LOW_POWER:
            self.beacon_interval = BeaconInterval.SLOW

        if self.mode == Mode.COMMS:
            # TODO: down link producer needs to create a dump to send down
            # self.dump_actuate_task.set_dump("dump")
            # self.dump_actuate_task.run = True
            self.beacon_interval = BeaconInterval.NEVER

        if self.mode == Mode.NORMAL:
            self.beacon_interval = BeaconInterval.FAST

        # TODO: figure out if beacon interval should be stored in SFR or in Control Task
        last_beacon_time: float = self.state_field_registry.get(StateField.APRS_LAST_BEACON_TIME)
        current_sys_time: float = self.state_field_registry.get(StateField.TIME)

        if current_sys_time - last_beacon_time > self.beacon_interval_lookup[self.beacon_interval]:
            pass
            # TODO: down link producer needs to create a beacon to send down
            # self.beacon_actuate_task.set_beacon("beacon")
            # self.beacon_actuate_task.run = True
