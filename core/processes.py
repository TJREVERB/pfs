import os
import subprocess

from helpers.power import Power
from helpers.mode import Mode


def power_watchdog(core, eps) -> None:
    """
    Constantly monitors eps power levels and switches Modes accordingly
    """
    while True:
        if eps.get_battery_bus_volts() >= Power.NORMAL.value and core.state != Mode.NORMAL:
            core.enter_normal_mode(
                f'Battery level at sufficient state: {eps.get_battery_bus_volts()}')
        elif eps.get_battery_bus_volts() < Power.NORMAL.value and core.state != Mode.LOW_POWER:
            core.enter_low_power_mode(
                f'Battery level at critical state: {eps.get_battery_bus_volts()}')


def is_first_boot() -> bool:
    """
    Returns True if it is determined that the computer is booting for the first time
    """
    cmd = subprocess.Popen(['last', 'reboot'], stdout=subprocess.PIPE, stderr=None)
    reboot_num = len([x for x in cmd.communicate()[0].splitlines() if x])-1
    return reboot_num == 1 #FIXME: Find a way to make this resilient for actual flight pi
