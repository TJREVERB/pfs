import logging
import os
import time

from enum import Enum
from functools import partial
from threading import Timer
from yaml import load

from core.threadhandler import ThreadHandler
from core.processes import power_watchdog, is_first_boot

from submodules.antenna_deploy import AntennaDeployer


class Mode(Enum):
    NORMAL = 0
    LOW_POWER = 1
    EMERGENCY = 2


class Power(Enum):
    STARTUP = 8.2
    NORMAL = 7.6
    EMERGENCY = 0


class Core:

    def __init__(self):
        if os.path.exists('config/config_custom.yml'):
            with open('config/config_custom.yml') as f:
                self.config = load(f)
        else:
            with open('config/config_default.yml') as f:
                self.config = load(f)

        self.logger = logging.getLogger("core")
        self.state = Mode.LOW_POWER
        self.submodules = {
            "antenna_deployer": AntennaDeployer(config=self.config),
            "aprs": None,
            "command_ingest": None,
            "eps": None,
            "iridium": None,
            "telemetry": None,
        }
        self.populate_dependencies()
        self.processes = {
            "power_monitor": ThreadHandler(target=partial(power_watchdog, args=self),
                                           name="power_monitor", parent_logger=self.logger),
            "telemetry_dump": Timer(interval=self.config['core']['dump_interval'],
                                    function=partial(self.submodules["telemetry"].dump))
        }

    def populate_dependencies(self):
        for submodule in self.submodules:
            if hasattr(self.submodules[submodule], 'set_modules'):
                self.submodules[submodule].set_modules({dependency: self.submodules[dependency]
                                                        for dependency in self.config[submodule]['depends_on']})

    def get_config(self):
        """Returns the configuration data from config_*.yml as a list"""
        return self.config

    def get_state(self):
        return self.state

    def enter_normal_mode(self, reason: str = '') -> None:
        """
        Enter normal power mode.
        :param reason: Reason for entering normal mode.
        """
        self.logger.warning(
            f"Entering normal mode{'  Reason: ' if reason else ''}{reason}")
        self.state = Mode.NORMAL
        for submodule in self.submodules:
            if hasattr(self.submodules[submodule], 'enter_normal_mode'):
                self.submodules[submodule].enter_normal_mode()

    def enter_low_power_mode(self, reason: str = '') -> None:
        """
        Enter low power mode.
        :param reason: Reason for entering low power mode.
        """
        self.logger.warning(
            f"Entering low_power mode{'  Reason: ' if reason else ''}{reason}")
        self.state = Mode.LOW_POWER
        for submodule in self.submodules:
            if hasattr(self.submodules[submodule], 'enter_low_power_mode'):
                self.submodules[submodule].enter_low_power_mode()

    def enter_emergency_mode(self, reason: str = '') -> None:
        """
        Enter emergency power mode.
        :param reason: Reason for entering emergency power mode.
        """
        self.logger.warning(
            f"Entering emergency mode{'  Reason: ' if reason else ''}{reason}")
        self.state = Mode.EMERGENCY
        for submodule in self.submodules:
            if hasattr(self.submodules[submodule], 'enter_emergency_mode'):
                self.submodules[submodule].enter_emergency_mode()

    def request(self, module_name):
        return self.submodules[module_name] if module_name in self.submodules.keys() else False

    def start(self):
        for submodule in self.config['core']['modules']['A']:
            if hasattr(self.submodules[submodule], 'start'):
                self.submodules[submodule].start()

        if is_first_boot():
            time.sleep(self.config['core']['sleep_interval'])

        for submodule in self.config['core']['modules']['B']:
            if hasattr(self.submodules[submodule], 'start'):
                self.submodules[submodule].start()

        for submodule in self.config['core']['modules']['C']:
            if hasattr(self.submodules[submodule], 'start'):
                self.submodules[submodule].start()

        while True:
            time.sleep(1)
