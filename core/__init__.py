import yaml
import time
import importlib
import logging
from . import mode
from . import power


logger = logging.getLogger()


with open('config.yml') as f:
    config = yaml.load(f)


def enter_normal_mode(reason: str='') -> None:
    global current_mode
    logger.info(f"Entering normal mode.{'  Reason: ' if reason else ''}{reason}")
    current_mode = mode.NORMAL
    # Trigger the module hooks
    for module in submodules:
        getattr(module, 'enter_normal_mode')()


def enter_low_power_mode(reason: str='') -> None:
    global current_mode
    logger.info(f"Entering low_power mode.{'  Reason: ' if reason else ''}{reason}")
    current_mode = mode.LOW_POWER
    # Trigger the module hooks
    for module in submodules:
        getattr(module, 'enter_low_power_mode')()


def enter_emergency_mode(reason: str='') -> None:
    global current_mode
    logger.info(f"Entering emergency mode.{'  Reason: ' if reason else ''}{reason}")
    current_mode = mode.EMERGENCY
    # Trigger the module hooks
    for module in submodules:
        getattr(module, 'enter_emergency_mode')()


def startup():
    global submodules
    logger.debug("Config:")
    logger.debug(config)
    # Load all the modules
    submodules = []
    for module in config['modules']:
        logger.debug(f'Loading module {module}')
        submodules.append(importlib.import_module(f'submodules.{module}'))
    # Trigger module startup
    for module in submodules:
        getattr(module, 'on_startup')()

    # Main loop?
    while True:
        sleep(1)



current_mode = mode.NORMAL
submodules = []
