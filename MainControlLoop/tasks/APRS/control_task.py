from MainControlLoop.lib.drivers.APRS import APRS
from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry, StateField
from MainControlLoop.lib.modes import Mode
from MainControlLoop.tasks.APRS.actuate_task import APRSActuateTask, APRSCriticalMessage
from MainControlLoop.tasks.DownLinkProducer import DownLinkProducer

from enum import Enum


class BeaconInterval(Enum):
    FAST = 30
    SLOW = 120
    CUSTOM = -1
    NEVER = 1

# TODO: implement all commands as an Enum


class APRSControlTask:

    def __init__(self, aprs: APRS, state_field_registry: StateFieldRegistry, mode: Mode, actuate_task: APRSActuateTask):
        self.aprs: APRS = aprs
        self.state_field_registry: StateFieldRegistry = state_field_registry
        self.mode: Mode = mode

        self.actuate_task: APRSActuateTask = actuate_task

    def execute(self, commands):
        # TODO: control task logic HAS NOT been written for boot/startup
        # TODO: control logic HAS NOT been written for parsing commands

        if self.mode == Mode.SAFE:
            self.state_field_registry.update(StateField.APRS_BEACON_INTERVAL, BeaconInterval.NEVER.value)
            # TODO: decide safe mode logic
            return

        if self.mode == Mode.STARTUP:
            # TODO: figure out how modules should communicate
            if len(commands) > 2 and commands[-1] == "pFS:AntennaDeployer;DEPLOYED;":
                self.actuate_task.set_critical_message(APRSCriticalMessage.ANTS_DEPLOYED)

        if self.mode == Mode.LOW_POWER:
            self.state_field_registry.update(StateField.APRS_BEACON_INTERVAL, BeaconInterval.SLOW.value)

        if self.mode == Mode.COMMS:
            # TODO: use the SFR Locker
            self.state_field_registry.update(StateField.APRS_BEACON_INTERVAL, BeaconInterval.NEVER.value)
            self.actuate_task.set_dump(DownLinkProducer.create_dump(self.state_field_registry))
            self.actuate_task.enable_dump()

        if self.mode == Mode.NORMAL:
            self.state_field_registry.update(StateField.APRS_BEACON_INTERVAL, BeaconInterval.FAST.value)

        command = ''.join(commands)
        if "TJ:C;APRS;SFR;;" in command:
            dump = DownLinkProducer.create_dump(self.state_field_registry)
            self.actuate_task.set_dump(dump)
            self.actuate_task.enable_dump()

        if "TJ:C;APRS;SFR_time;" in command:
            # TODO: implement SFR Locker here
            pass

        if "TJ:C;APRS;SF;" in command:
            # TODO: implement response message here
            pass

        if "TJ:C;APRS;reset;;" in command:
            # TODO: implement APRS hard reset here
            pass

        interval = self.state_field_registry.get(StateField.APRS_BEACON_INTERVAL)
        last_beacon_time: float = self.state_field_registry.get(StateField.APRS_LAST_BEACON_TIME)
        current_sys_time: float = self.state_field_registry.get(StateField.TIME)

        if "TJ:C;APRS;beacon;;" in command or current_sys_time - last_beacon_time > interval:
            beacon = DownLinkProducer.create_beacon(self.state_field_registry)
            self.actuate_task.set_beacon(beacon)
            self.actuate_task.enable_beacon()
