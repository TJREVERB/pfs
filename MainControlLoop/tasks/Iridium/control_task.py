from MainControlLoop.lib.drivers.Iridium import Iridium
from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry, StateField, StateFieldRegistryLocker
from MainControlLoop.lib.modes import Mode
from MainControlLoop.tasks.Iridium.actuate_task import IridiumActuateTask
from MainControlLoop.tasks.DownLinkProducer import DownLinkProducer

import re
from enum import Enum


class DumpInterval(Enum):
    NORMAL = 120
    NEVER = -1


class IridiumControlTask:

    def __init__(self, iridium: Iridium, state_field_registry: StateFieldRegistry, actuate_task: IridiumActuateTask):
        self.iridium: Iridium = iridium
        self.state_field_registry: StateFieldRegistry = state_field_registry
        self.mode: Mode = Mode.BOOT

        self.actuate_task: IridiumActuateTask = actuate_task

    def execute(self):
        current_sys_time: float = self.state_field_registry.get(StateField.TIME)

        if self.mode == Mode.SAFE:
            # TODO: safe mode implementation
            return

        if self.mode != Mode.NORMAL:
            self.state_field_registry.update(StateField.IRIDIUM_DUMP_INTERVAL, DumpInterval.NEVER)
            return
        self.state_field_registry.update(StateField.IRIDIUM_DUMP_INTERVAL, DumpInterval.NORMAL)

        interval = self.state_field_registry.get(StateField.IRIDIUM_DUMP_INTERVAL)
        last_beacon_time: float = self.state_field_registry.get(StateField.IRIDIUM_LAST_DUMP_TIME)

        if current_sys_time - last_beacon_time > interval:
            dump = DownLinkProducer.create_dump(self.state_field_registry)
            self.actuate_task.set_dump(dump)
            self.actuate_task.enable_dump()

        self.actuate_task.enable_geolocation()
        self.actuate_task.enable_signal_strength()
