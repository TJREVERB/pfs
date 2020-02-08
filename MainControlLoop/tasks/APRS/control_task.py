from MainControlLoop.lib.drivers.APRS import APRS
from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry, StateField
from MainControlLoop.lib.modes import Mode
from MainControlLoop.tasks.APRS.beacon_actuate_task import APRSBeaconActuateTask
from MainControlLoop.tasks.APRS.dump_actuate_task import APRSDumpActuateTask
from MainControlLoop.tasks.APRS.crticial_message_actuate_task import APRSCriticalMessageActuateTask
from MainControlLoop.tasks.DownLinkProducer import DownLinkProducer

from enum import Enum


class BeaconInterval(Enum):
    FAST = 30
    SLOW = 120
    CUSTOM = -1
    NEVER = 1


class APRSControlTask:

    def __init__(self, aprs: APRS, state_field_registry: StateFieldRegistry, mode: Mode, beacon_actuate_task: APRSBeaconActuateTask, dump_actuate_task: APRSDumpActuateTask, critical_message_actuate_task: APRSCriticalMessageActuateTask):
        self.aprs: APRS = aprs
        self.state_field_registry: StateFieldRegistry = state_field_registry
        self.mode: Mode = mode

        self.beacon_actuate_task: APRSBeaconActuateTask = beacon_actuate_task
        self.dump_actuate_task: APRSDumpActuateTask = dump_actuate_task
        self.critical_message_actuate_task: APRSCriticalMessageActuateTask = critical_message_actuate_task

    def execute(self, commands):
        # TODO: control task logic HAS NOT been written for boot/startup
        # TODO: control logic HAS NOT been written for parsing commands

        if self.mode == Mode.SAFE:
            self.state_field_registry.update(StateField.APRS_BEACON_INTERVAL, BeaconInterval.NEVER.value)
            # TODO: decide safe mode logic
            return

        if self.mode == Mode.LOW_POWER:
            self.state_field_registry.update(StateField.APRS_BEACON_INTERVAL, BeaconInterval.SLOW.value)

        if self.mode == Mode.COMMS:
            # TODO: use the SFR Locker
            self.state_field_registry.update(StateField.APRS_BEACON_INTERVAL, BeaconInterval.NEVER.value)
            self.dump_actuate_task.set_dump(DownLinkProducer.create_dump(self.state_field_registry))
            self.dump_actuate_task.run = True

        if self.mode == Mode.NORMAL:
            self.state_field_registry.update(StateField.APRS_BEACON_INTERVAL, BeaconInterval.FAST.value)

        interval = self.state_field_registry.get(StateField.APRS_BEACON_INTERVAL)
        last_beacon_time: float = self.state_field_registry.get(StateField.APRS_LAST_BEACON_TIME)
        current_sys_time: float = self.state_field_registry.get(StateField.TIME)

        if current_sys_time - last_beacon_time > interval:
            beacon = DownLinkProducer.create_beacon(self.state_field_registry)
            self.beacon_actuate_task.set_beacon(beacon)
            self.beacon_actuate_task.run = True
