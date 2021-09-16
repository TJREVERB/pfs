from MainControlLoop.lib.drivers.APRS import APRS
from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry, StateField, StateFieldRegistryLocker
from MainControlLoop.lib.modes import Mode
from MainControlLoop.tasks.APRS.actuate_task import APRSActuateTask, APRSCriticalMessage
from MainControlLoop.tasks.DownLinkProducer import DownLinkProducer

import re
from enum import Enum


class BeaconInterval(Enum):
    FAST = 30
    SLOW = 120
    CUSTOM = -1
    NEVER = 1


class APRSCommands(Enum):
    BEACON = r"TJ:C;APRS;beacon;;"
    BEACON_INTERVAL = r"TJ:C;APRS;beacon_interval;\d+;"
    SFR = r"TJ:C;APRS;SFR;;"
    SFR_TIME = r"TJ:C;APRS;SFR_time;\d+;"
    SF = r"TJ:C;APRS;SF;[\w\d_]+;"
    RESET = r"TJ:C;APRS;reset;;"

    ANTENNA_DEPLOY_INITIATED = r"pFS:AntennaDeployer;DEPLOYED;"


class APRSControlTask:

    def __init__(self, aprs: APRS, state_field_registry: StateFieldRegistry, locker: StateFieldRegistryLocker,
                 actuate_task: APRSActuateTask):
        self.aprs: APRS = aprs
        self.state_field_registry: StateFieldRegistry = state_field_registry
        self.locker = locker
        self.mode: Mode = Mode.BOOT

        self.actuate_task: APRSActuateTask = actuate_task

    def execute(self, commands):
        # TODO: control task logic HAS NOT been decided for boot/startup/safe mode

        current_sys_time: float = self.state_field_registry.get(StateField.TIME)
        command_joined = ''.join(commands)  # join all commands from list to single string

        if self.mode == Mode.SAFE:  # switch off beacon if in safe mode
            self.state_field_registry.update(StateField.APRS_BEACON_INTERVAL, BeaconInterval.NEVER.value)
            return

        if self.mode == Mode.STARTUP: # if in startup mode and antenna has been deployed, enable a critical message that the antenna has been deployed
            if re.search(APRSCommands.ANTENNA_DEPLOY_INITIATED.value, command_joined) is not None:
                self.actuate_task.set_critical_message(APRSCriticalMessage.ANTS_DEPLOYED)
                self.actuate_task.enable_critical_message()

        if self.mode == Mode.LOW_POWER:  # set beacon interval to slow if in low power mode
            self.state_field_registry.update(StateField.APRS_BEACON_INTERVAL, BeaconInterval.SLOW.value)

        if self.mode == Mode.COMMS:  # if in comms mode, turn off beacon, enable aprs to dump statefield
            self.state_field_registry.update(StateField.APRS_BEACON_INTERVAL, BeaconInterval.NEVER.value)

            dump = self.locker.find(current_sys_time)
            self.actuate_task.set_dump(dump)
            self.actuate_task.enable_dump()

        if self.mode == Mode.NORMAL:  # if in normal mode, set beacon interval to fast
            self.state_field_registry.update(StateField.APRS_BEACON_INTERVAL, BeaconInterval.FAST.value)

        if re.search(APRSCommands.SFR.value, command_joined) is not None:  # if sfr method is in command_joined, create  adump for the current statefield
            dump = DownLinkProducer.create_dump(self.state_field_registry)
            self.actuate_task.set_dump(dump)
            self.actuate_task.enable_dump()

        match = re.search(APRSCommands.SFR_TIME.value, command_joined)   
        if match is not None: # if sfr time in command_joined, find previous dump and enable dunp
            cmd = command_joined[match.start(): match.end()]
            arg = cmd.split(";")[-2]
            timestamp = float('0' + re.sub(r"[^\d.]", '', arg))

            dump = self.locker.find(timestamp)
            self.actuate_task.set_dump(dump)
            self.actuate_task.enable_dump()

        match = re.search(APRSCommands.SF.value, command_joined)
        if match is not None:
            cmd = command_joined[match.start(): match.end()]
            arg = cmd.split(";")[-2]
            try:
                state_field = StateField(arg)
                response = DownLinkProducer.create_response(self.state_field_registry, state_field)
                if response != '':
                    self.actuate_task.set_response(response)
                    self.actuate_task.enable_response()
            except:
                pass

        if re.search(APRSCommands.RESET.value, command_joined) is not None:
            self.state_field_registry.update(StateField.APRS_BEACON_INTERVAL, BeaconInterval.NEVER)
            self.actuate_task.enable_reset()

        interval = self.state_field_registry.get(StateField.APRS_BEACON_INTERVAL)
        last_beacon_time: float = self.state_field_registry.get(StateField.APRS_LAST_BEACON_TIME)

        if current_sys_time - last_beacon_time > interval or re.search(APRSCommands.BEACON.value,
                                                                       command_joined) is not None:  # create a beacon with state field registry if over time interval or beacon value in command
            beacon = DownLinkProducer.create_beacon(self.state_field_registry)
            self.actuate_task.set_beacon(beacon)
            self.actuate_task.enable_beacon()
