from core import Power
from core import Mode


def power_watchdog(core):
    eps = core.request_module("eps")
    while True:
        if eps.get_battery_bus_volts() >= Power.NORMAL.value and core.state != Mode.NORMAL:
            core.enter_normal_mode(
                f'Battery level at sufficient state: {eps.get_battery_bus_volts()}')
        elif eps.get_battery_bus_volts() < Power.NORMAL.value and core.state != Mode.LOW_POWER:
            core.enter_low_power_mode(
                f'Battery level at critical state: {eps.get_battery_bus_volts()}')