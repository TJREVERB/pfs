import importlib
import logging
import os

import yaml

from core.mode import Mode
from core.power import Power
from submodules import eps

config = None  # Prevents IDE from throwing errors about not finding `config`
logger = logging.getLogger("ROOT")


def load_config():
    """
    Loads a YAML file to be used as the `config`.
    If `config_custom.yml` exists, use that (this is user-configurable).
    Else, use `config_default.yml`. This should not be changed while testing.
    """

    # `config_custom.yml` (custom configuration file) exists
    if os.path.exists('config_custom.yml'):
        # TODO: be resilient to I/O errors (e.g. persistent storage is ded)
        with open('config_custom.yml') as f:
            config = yaml.load(f)
    else:
        # Custom configuration does not exist, use `config_default.yml`
        with open('config_default.yml') as f:
            config = yaml.load(f)

    return config


def get_state():
    return state


def enter_normal_mode(reason: str = '') -> None:
    """
    Enter normal power mode.
    :param reason: Reason for entering normal mode.
    """
    global state
    logger.warning(
        f"Entering normal mode{'  Reason: ' if reason else ''}{reason}")
    state = Mode.NORMAL

    # Trigger the module hooks
    for module in submodules:
        if hasattr(module, 'enter_normal_mode'):
            getattr(module, 'enter_normal_mode')()


def enter_low_power_mode(reason: str = '') -> None:
    """
    Enter low power mode.
    :param reason: Reason for entering low power mode.
    """
    global state
    logger.warning(
        f"Entering low_power mode{'  Reason: ' if reason else ''}{reason}")
    state = Mode.LOW_POWER

    for module in submodules:  # Trigger the module hooks
        if hasattr(module, 'enter_low_power_mode'):
            getattr(module, 'enter_low_power_mode')()


def enter_emergency_mode(reason: str = '') -> None:
    """
    Enter emergency power mode.
    :param reason: Reason for entering emergency power mode.
    """
    global state
    logger.warning(
        f"Entering emergency mode{'  Reason: ' if reason else ''}{reason}")
    state = Mode.EMERGENCY

    for module in submodules:  # Trigger the module hooks
        if hasattr(module, 'enter_emergency_mode'):
            getattr(module, 'enter_emergency_mode')()


def check_first_boot():  # TODO: IF EMPROM SAYS FIRST BOOT WAIT 30 MINUTES ELSE CONTINUE
    # if eeprom.get("FIRST_BOOT") is None or eeprom.get("FIRST_BOOT") == True:
    #    eeprom.add("FIRST BOOT", True) #FIXME eeprom stuff
    #    time.sleep(1800)
    pass


def cold_start():  # Waits till startup voltage is reached before continuing
    while eps.get_battery_bus_volts() < Power.STARTUP:
        if eps.get_battery_bus_volts() >= Power.STARTUP:
            return
        else:
            continue


def power_watchdog():
    while True:
        if eps.get_battery_bus_volts() >= Power.NORMAL:
            enter_normal_mode(
                f'Battery level at sufficient state: {eps.get_battery_bus_volts()}')
        elif eps.get_battery_bus_volts() < Power.NORMAL:
            enter_low_power_mode(
                f'Battery level at critical state: {eps.get_battery_bus_volts()}')


def start():
    global submodules, config, state
    # Load `config` from either default file or persistent config
    config = load_config()
    state = None

    # logger.debug(f"Config: {config}")

    # Ensure that logs directory exists
    if not os.path.exists(config['core']['log_dir']):
        os.mkdir(config['core']['log_dir'])

    # Loop through all active modules in YAML config file, add them to `config`
    submodules = []
    level_a = []
    level_b = []
    level_c = []
    if config['core']['modules'] is not None:
        if config['core']['modules']['A'] is not None:
            for submodule in config['core']['modules']['A']:
                logger.debug(f'Loading module: {submodule}')
                level_a.append(importlib.import_module(
                    f'submodules.{submodule}'))
            submodules.append(level_a)
        if config['core']['modules']['B'] is not None:
            for submodule in config['core']['modules']['B']:
                logger.debug(f'Loading module: {submodule}')
                level_b.append(importlib.import_module(
                    f'submodules.{submodule}'))
            submodules.append(level_b)
        if config['core']['modules']['C'] is not None:
            for submodule in config['core']['modules']['C']:
                logger.debug(f'Loading module: {submodule}')
                level_c.append(importlib.import_module(
                    f'submodules.{submodule}'))
            submodules.append(level_c)
        logger.debug(submodules)

    # Trigger module start
    for i in submodules[0]:
        logger.debug(f'Starting level A module {i}')
        if hasattr(i, 'start'):
            getattr(i, 'start')()
    check_first_boot()
    for i in submodules[1]:
        logger.debug(f'Starting level B module {i}')
        if hasattr(i, 'start'):
            getattr(i, 'start')()
    cold_start()
    for i in submodules[2]:
        logger.debug(f'Starting level C module {i}')
        if hasattr(i, 'start'):
            getattr(i, 'start')

    enter_normal_mode()
    logger.debug("Entering main loop")

    # MAIN LOOP
    # power_watchdog()
