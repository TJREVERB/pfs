import importlib
import logging
import os
import time

import yaml

from helpers.threadhandler import ThreadHandler
from . import mode
from . import power
from submodules import eps
from submodules import eeprom

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


def enter_normal_mode(reason: str = '') -> None:
    """
    Enter normal power mode.
    :param reason: Reason for entering normal mode.
    """
    global current_mode
    logger.warning(
        f"Entering normal mode{'  Reason: ' if reason else ''}{reason}")
    current_mode = mode.NORMAL

    # Trigger the module hooks
    for module in submodules:
        if hasattr(module, 'enter_normal_mode'):
            getattr(module, 'enter_normal_mode')()


def enter_low_power_mode(reason: str = '') -> None:
    """
    Enter low power mode.
    :param reason: Reason for entering low power mode.
    """
    global current_mode
    logger.warning(
        f"Entering low_power mode{'  Reason: ' if reason else ''}{reason}")
    current_mode = mode.LOW_POWER

    for module in submodules:  # Trigger the module hooks
        if hasattr(module, 'enter_low_power_mode'):
            getattr(module, 'enter_low_power_mode')()


def enter_emergency_mode(reason: str = '') -> None:
    """
    Enter emergency power mode.
    :param reason: Reason for entering emergency power mode.
    """
    global current_mode
    logger.warning(
        f"Entering emergency mode{'  Reason: ' if reason else ''}{reason}")
    current_mode = mode.EMERGENCY

    for module in submodules:  # Trigger the module hooks
        if hasattr(module, 'enter_emergency_mode'):
            getattr(module, 'enter_emergency_mode')()


def check_first_boot():  # TODO: IF EMPROM SAYS FIRST BOOT WAIT 30 MINUTES ELSE CONTINUE
    if eeprom.get("FIRST_BOOT") is None or eeprom.get("FIRST_BOOT") == True:
        eeprom.add("FIRST BOOT", True) #FIXME eeprom stuff
        time.sleep(1800)


def cold_start():  # TODO WAIT UNTIL POWER THRESHOLD IS REACHED
    while eps.get_bcr1_volts() < power.STARTUP:
        continue


def start():
    global submodules
    # Load `config` from either default file or persistent config
    config = load_config()

    logger.debug("Config: ", config)

    # Ensure that logs directory exists
    if not os.path.exists(config['core']['log_dir']):
        os.mkdir(config['core']['log_dir'])

    # Loop through all active modules in YAML config file, add them to `config`
    submodules = []
    if config['core']['modules'] is not None:
        if config['core']['modules']['A'] is not None:
            level_a = []
            for submodule in config['core']['modules']['A']:
                logger.debug(f'Loading module: {submodule}')
                level_a.append(importlib.import_module(
                    f'submodules.{submodule}'))
            submodules.append(level_a)
        if config['core']['modules']['B'] is not None:
            level_b = []
            for submodule in config['core']['modules']['B']:
                logger.debug(f'Loading module: {submodule}')
                level_b.append(importlib.import_module(
                    f'submodules.{submodule}'))
            submodules.append(level_b)
        if config['core']['modules']['C'] is not None:
            level_c = []
            for submodule in config['core']['modules']['C']:
                logger.debug(f'Loading module: {submodule}')
                level_c.append(importlib.import_module(
                    f'submodules.{submodule}'))
            submodules.append(level_c)
        logger.debug(submodules)

    # Trigger module start
    for module in submodules[0]:
        logger.debug(f'Starting level A module {module}')
        if hasattr(module, 'start'):
            getattr(module, 'start')()
    check_first_boot()
    for module in submodules[1]:
        logger.debug(f'Starting level B module {module}')
        if hasattr(module, 'start'):
            getattr(module, 'start')()
    cold_start()
    for module in submodules[2]:
        logger.debug(f'Starting level C module {module}')
        if hasattr(module, 'start'):
            getattr(module, 'start')

    enter_normal_mode()  # Enter normal mode
    logger.debug("Entering main loop")

    # MAIN LOOP
    while True:
        if eps.get_bcr1_volts() >= power.NORMAL:
            enter_normal_mode()
        elif eps.get_bcr1_volts() < power.NORMAL:
            if eps.get_bcr1_volts() > power.LOW:
                enter_low_power_mode()
            if eps.get_bcr1_volts() < power.LOW:
                enter_emergency_mode()
            # TODO: ADD MORE CASES


current_mode = mode.NORMAL  # Default power mode
submodules = []  # List of all active modules
