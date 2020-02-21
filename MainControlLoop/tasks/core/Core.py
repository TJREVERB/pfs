from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry, ErrorFlag, StateField
from MainControlLoop.lib.modes import Mode
from MainControlLoop.tasks.APRS import APRSTask


class Core:

    LOW_POWER_BATTERY_THRESHOLD = 8
    NORMAL_BATTERY_THRESHOLD = 9

    ENTER_SAFE_COMMAND = "TJ:C;CORE;safe;;"
    ENTER_COMMS_COMMAND = "TJ:C;CORE;comms;;"

    def __init__(self, state_field_registry: StateFieldRegistry, aprs_task: APRSTask):
        self.state_field_registry: StateFieldRegistry = state_field_registry
        self.mode = Mode.BOOT

        self.aprs_task = aprs_task

    def control(self, commands):
        command = "".join(commands)

        if self.mode == Mode.NORMAL:
            self.dispatch_normal(command)

    def dispatch_normal(self, command):
        if self.state_field_registry.critical_failure() or self.ENTER_SAFE_COMMAND in command:
            self.dispatch_safe()
            return

        if self.state_field_registry.get(StateField.VPCMBATV) < self.LOW_POWER_BATTERY_THRESHOLD:
            self.dispatch_low_power(command)
            return

        if self.ENTER_COMMS_COMMAND in command:
            self.dispatch_comms()

        self.aprs_task.set_mode(Mode.NORMAL)

    def dispatch_low_power(self, command):
        if self.state_field_registry.critical_failure() or self.ENTER_SAFE_COMMAND in command:
            self.dispatch_safe()
            return

        if self.state_field_registry.get(StateField.VPCMBATV) > self.NORMAL_BATTERY_THRESHOLD:
            self.dispatch_normal(command)
            return

        self.aprs_task.set_mode(Mode.LOW_POWER)

    def dispatch_safe(self):
        return

    def dispatch_comms(self):
        return

    def dispatch_boot(self):
        if self.state_field_registry.get(StateField.BOOT_WAIT_COMPLETE):
            self.dispatch_startup()
            return

        self.aprs_task.set_mode(Mode.BOOT)

    def dispatch_startup(self):
        return
