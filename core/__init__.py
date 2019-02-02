import importlib
import logging
import os
import time

import yaml

from helpers.threadhandler import ThreadHandler
from . import mode
from . import power

config = None  # Prevents IDE from throwing errors about not finding `config`


def load_config():
    """
    Loads a YAML file to be used as the `config`.
    If `config_custom.yml` exists, use that (this is user-configurable).
    Else, use `config_default.yml`. This should not be changed while testing.
    """
    global config
    if os.path.exists('config_custom.yml'):  # `config_custom.yml` (custom configuration file) exists
        with open('config_custom.yml') as f:  # TODO: be resilient to I/O errors (e.g. persistent storage is ded)
            config = yaml.load(f)
    else:
        with open('config_default.yml') as f:  # Custom configuration does not exist, use `config_default.yml`
            config = yaml.load(f)


def config_saver():
    """
    Save `config` every so often.
    """
    while True:
        time.sleep(config['core']['config_save_interval'])  # TODO: put a lock on config saving / make use of remount
        with open('config_custom.yml', 'w') as f:
            yaml.dump(f)


def enter_normal_mode(reason: str = '') -> None:
    """
    Enter normal power mode.
    :param reason: Reason for entering normal mode.
    """
    global current_mode
    logging.info(f"Entering normal mode.{'  Reason: ' if reason else ''}{reason}")
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
    logging.warning(f"Entering low_power mode.{'  Reason: ' if reason else ''}{reason}")
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
    logging.critical(f"Entering emergency mode.{'  Reason: ' if reason else ''}{reason}")
    current_mode = mode.EMERGENCY

    for module in submodules:  # Trigger the module hooks
        if hasattr(module, 'enter_emergency_mode'):
            getattr(module, 'enter_emergency_mode')()


def start():
    global submodules
    # Load `config` from either default file or persistent config
    load_config()
    logging.debug("Config:")
    logging.debug(config)

    # Ensure that logs directory exists
    if not os.path.exists(config['core']['log_dir']):
        os.mkdir(config['core']['log_dir'])

    # Loop through all active modules in YAML config file, add them to `config`
    submodules = []
    for module in config['core']['modules']:
        logging.debug(f'Loading module {module}')
        submodules.append(importlib.import_module(f'submodules.{module}'))

    # Trigger module start
    for module in submodules:
        if hasattr(module, 'start'):
            getattr(module, 'start')()

    enter_normal_mode()  # Enter normal mode
    logging.debug("Entering main loop.")

    # MAIN LOOP
    while True:
        time.sleep(1)


current_mode = mode.NORMAL  # Default power mode
submodules = []  # List of all active modules
