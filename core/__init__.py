import importlib
import logging
import os
import time

import yaml

from . import mode
from . import power

with open('config.yml') as f:
    config = yaml.load(f)


def enter_normal_mode(reason: str = '') -> None:
    global current_mode
    logging.info(f"Entering normal mode.{'  Reason: ' if reason else ''}{reason}")
    current_mode = mode.NORMAL
    # Trigger the module hooks
    for module in submodules:
        if hasattr(module, 'enter_normal_mode'):
            getattr(module, 'enter_normal_mode')()


def enter_low_power_mode(reason: str = '') -> None:
    global current_mode
    logging.info(f"Entering low_power mode.{'  Reason: ' if reason else ''}{reason}")
    current_mode = mode.LOW_POWER
    # Trigger the module hooks
    for module in submodules:
        if hasattr(module, 'enter_low_power_mode'):
            getattr(module, 'enter_low_power_mode')()


def enter_emergency_mode(reason: str = '') -> None:
    global current_mode
    logging.info(f"Entering emergency mode.{'  Reason: ' if reason else ''}{reason}")
    current_mode = mode.EMERGENCY
    # Trigger the module hooks
    for module in submodules:
        if hasattr(module, 'enter_emergency_mode'):
            getattr(module, 'enter_emergency_mode')()


def startup():
    global submodules
    logging.debug("Config:")
    logging.debug(config)
    # Ensure that logs directory exists
    if not os.path.exists(config['core']['log_dir']):
        os.mkdir(config['core']['log_dir'])
    # Load all the modules
    submodules = []
    for module in config['core']['modules']:
        logging.debug(f'Loading module {module}')
        submodules.append(importlib.import_module(f'submodules.{module}'))
    # Trigger module startup
    for module in submodules:
        if hasattr(module, 'on_startup'):
            getattr(module, 'on_startup')()
    logging.debug("Entering main loop.")
    # Main loop?
    while True:
        time.sleep(1)


current_mode = mode.NORMAL
submodules = []
