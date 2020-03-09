import time
from enum import Enum
from smbus2 import SMBus, i2c_msg
from MainControlLoop.lib.devices import Device


class AntennaDeployerCommand(Enum):
    SYSTEM_RESET = 0xAA
    WATCHDOG_RESET = 0xCC

    ARM_ANTS = 0xAD
    DISARM_ANTS = 0xAC

    DEPLOY_1 = 0xA1
    DEPLOY_2 = 0xA2
    DEPLOY_3 = 0xA3
    DEPLOY_4 = 0xA4

    AUTO_DEPLOY = 0xA5
    CANCEL_DEPLOY = 0xA9

    DEPLOY_1_OVERRIDE = 0xBA
    DEPLOY_2_OVERRIDE = 0xBB
    DEPLOY_3_OVERRIDE = 0xBC
    DEPLOY_4_OVERRIDE = 0xBD

    GET_TEMP = 0xC0
    GET_STATUS = 0xC3

    GET_COUNT_1 = 0xB0
    GET_COUNT_2 = 0xB1
    GET_COUNT_3 = 0xB2
    GET_COUNT_4 = 0xB3

    GET_UPTIME_1 = 0xB4
    GET_UPTIME_2 = 0xB5
    GET_UPTIME_3 = 0xB6
    GET_UPTIME_4 = 0xB7


class AntennaDeployer(Device):
    BUS_NUMBER = 1
    PRIMARY_ADDRESS = 0x31
    SECONDARY_ADDRESS = 0x32
    EXPECTED_BYTES = {
        AntennaDeployerCommand.SYSTEM_RESET: 0,
        AntennaDeployerCommand.WATCHDOG_RESET: 0,

        AntennaDeployerCommand.ARM_ANTS: 0,
        AntennaDeployerCommand.DISARM_ANTS: 0,

        AntennaDeployerCommand.DEPLOY_1: 0,
        AntennaDeployerCommand.DEPLOY_2: 0,
        AntennaDeployerCommand.DEPLOY_3: 0,
        AntennaDeployerCommand.DEPLOY_4: 0,

        AntennaDeployerCommand.AUTO_DEPLOY: 0,
        AntennaDeployerCommand.CANCEL_DEPLOY: 0,

        AntennaDeployerCommand.DEPLOY_1_OVERRIDE: 0,
        AntennaDeployerCommand.DEPLOY_2_OVERRIDE: 0,
        AntennaDeployerCommand.DEPLOY_3_OVERRIDE: 0,
        AntennaDeployerCommand.DEPLOY_4_OVERRIDE: 0,

        AntennaDeployerCommand.GET_TEMP: 2,
        AntennaDeployerCommand.GET_STATUS: 2,

        AntennaDeployerCommand.GET_COUNT_1: 1,
        AntennaDeployerCommand.GET_COUNT_2: 1,
        AntennaDeployerCommand.GET_COUNT_3: 1,
        AntennaDeployerCommand.GET_COUNT_4: 1,

        AntennaDeployerCommand.GET_UPTIME_1: 2,
        AntennaDeployerCommand.GET_UPTIME_2: 2,
        AntennaDeployerCommand.GET_UPTIME_3: 2,
        AntennaDeployerCommand.GET_UPTIME_4: 2,
    }

    def __init__(self):
        super().__init__("AntennaDeployer")
        self.bus = SMBus()

    def write(self, command: AntennaDeployerCommand, parameter: int) -> bool or None:
        """
        Wrapper for SMBus write word data
        :param command: (AntennaDeployerCommand) The antenna deployer command to run
        :param parameter: (int) The parameter to pass in to the command (usually 0x00)
        :return: (bool or None) success
        """
        if type(command) != AntennaDeployerCommand:
            return

        try:
            self.bus.open(self.BUS_NUMBER)
            self.bus.write_word_data(self.PRIMARY_ADDRESS, command.value, parameter)
            self.bus.close()
        except:
            return False

        return True

    def read(self, command: AntennaDeployerCommand) -> bytes or None:
        """
        Wrapper for SMBus to read from AntennaDeployer
        :param command: (AntennaDeployerCommand) The antenna deployer command to run
        :return: (ctypes.LP_c_char, bool) buffer, success
        """
        if type(command) != AntennaDeployerCommand:
            return

        success = self.write(command, 0x00)
        if not success:
            return None, False

        time.sleep(0.5)
        try:
            i2c_obj = i2c_msg.read(self.PRIMARY_ADDRESS, self.EXPECTED_BYTES[command])
            self.bus.open(self.BUS_NUMBER)
            self.bus.i2c_rdwr(i2c_obj)
            self.bus.close()
            return i2c_obj.buf, True
        except:
            return None, False

    def functional(self):
        """
        :return: (bool) i2c file opened by SMBus
        """
        return self.bus.fd is not None

    def reset(self):
        """
        Resets the Microcontroller on the ISIS Antenna Deployer
        :return: (bool) no error
        """
        try:
            self.bus.open(self.BUS_NUMBER)
            self.write(AntennaDeployerCommand.SYSTEM_RESET, 0x00)
            self.bus.close()
            return True
        except:
            return False

    def disable(self):
        """
        Disarms the ISIS Antenna Deployer
        """
        try:
            self.bus.open(self.BUS_NUMBER)
            self.write(AntennaDeployerCommand.DISARM_ANTS, 0x00)
            self.bus.close()
            return True
        except:
            return False

    def enable(self):
        """
        Arms the ISIS Antenna Deployer
        """
        try:
            self.bus.open(self.BUS_NUMBER)
            self.write(AntennaDeployerCommand.ARM_ANTS, 0x00)
            self.bus.close()
            return True
        except:
            return False
