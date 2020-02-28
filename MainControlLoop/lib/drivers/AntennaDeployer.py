import time
from enum import Enum
from smbus2 import SMBus
from smbus2 import i2c_msg
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
    DEPLOY_1_OVERRIDE = 0xBA
    DEPLOY_2_OVERRIDE = 0xBB
    DEPLOY_3_OVERRIDE = 0xBC
    DEPLOY_4_OVERRIDE = 0xBD
    CANCEL_DEPLOY = 0xA9
    GET_TEMP = 0xC0
    GET_STATUS = 0xC3
    GET_UPTIME_SYS = 0xC6
    GET_TELEMETRY = 0xC7
    GET_COUNT_1 = 0xB0
    GET_COUNT_2 = 0xB1
    GET_COUNT_3 = 0xB2
    GET_COUNT_4 = 0xB3
    GET_UPTIME_1 = 0xB4
    GET_UPTIME_2 = 0xB5
    GET_UPTIME_3 = 0xB6
    GET_UPTIME_4 = 0xB7


class AntennaDeployerReturnBytes(Enum):
    AntennaDeployerCommand.SYSTEM_RESET = 0
    AntennaDeployerCommand.WATCHDOG_RESET = 0
    AntennaDeployerCommand.ARM_ANTS = 0
    AntennaDeployerCommand.DISARM_ANTS = 0
    AntennaDeployerCommand.DEPLOY_1 = 0
    AntennaDeployerCommand.DEPLOY_2 = 0
    AntennaDeployerCommand.DEPLOY_3 = 0
    AntennaDeployerCommand.DEPLOY_4 = 0
    AntennaDeployerCommand.AUTO_DEPLOY = 0
    AntennaDeployerCommand.DEPLOY_1_OVERRIDE = 0
    AntennaDeployerCommand.DEPLOY_2_OVERRIDE = 0
    AntennaDeployerCommand.DEPLOY_3_OVERRIDE = 0
    AntennaDeployerCommand.DEPLOY_4_OVERRIDE = 0
    AntennaDeployerCommand.CANCEL_DEPLOY = 0
    AntennaDeployerCommand.GET_TEMP = 2
    AntennaDeployerCommand.GET_STATUS = 2
    #    AntennaDeployerCommand.GET_UPTIME_SYS = None
    #    AntennaDeployerCommand.GET_TELEMETRY = None
    AntennaDeployerCommand.GET_COUNT_1 = 1
    AntennaDeployerCommand.GET_COUNT_2 = 1
    AntennaDeployerCommand.GET_COUNT_3 = 1
    AntennaDeployerCommand.GET_COUNT_4 = 1
    AntennaDeployerCommand.GET_UPTIME_1 = 2
    AntennaDeployerCommand.GET_UPTIME_2 = 2
    AntennaDeployerCommand.GET_UPTIME_3 = 2
    AntennaDeployerCommand.GET_UPTIME_4 = 2


# TODO: Create a similar enum, but instead of return bytes, it should be params (length of arguments passed when writing)

class AntennaDeployer(Device):

    BUS_NAME = '/dev/i2c-2'

    def __init__(self):
        super().__init__("antenna_deployer")
        self.bus = SMBus(1)
        self.primary_address = 0x31
        self.secondary_address = 0x32

    def write_i2c_word_data(self, command: AntennaDeployerCommand, data: int) -> bool:
        if type(command) != AntennaDeployerCommand:
            return False

        # FIXME: whenever self.bus is used the line before should use self.bus.open, and the line after should close
        self.bus.write_word_data(self.primary_address, command.value, data)
        return True

    def read_i2c_data(self, command: AntennaDeployerCommand) -> bytes or None:
        if type(command) != AntennaDeployerCommand:
            return None

        # FIXME: self.bus
        bus.write_word_data(self.primary_address, command.value, 0x00)
        time.sleep(0.5)
        num_bytes = AntennaDeployerReturnBytes.command.value

        # This code allows us to read more than just one byte from the antenna deployer
        i2c_obj = i2c_msg.read(self.primary_address, num_bytes)
        return self.bus.i2c_rdwr(i2c_obj)

    def deploy(self, register: AntennaDeployerCommand):
        if not isinstance(register, AntennaDeployerCommand):
            return

        # FIXME what happens if arm is called multiple times?
        self.write_i2c_word_data(AntennaDeployerCommand.ARM_ANTS)
        self.write_i2c_word_data(AntennaDeployerCommand.DEPLOY_1)
        self.write_i2c_word_data(AntennaDeployerCommand.DEPLOY_2)
        self.write_i2c_word_data(AntennaDeployerCommand.DEPLOY_3)
        self.write_i2c_word_data(AntennaDeployerCommand.DEPLOY_4)

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
            self.bus.open(self.BUS_NAME)
        except:
            return False
        self.write_i2c_word_data(AntennaDeployerCommand.SYSTEM_RESET)

    def disable(self):
        """
        Disarms the ISIS Antenna Deployer
        """
        try:
            self.bus.open(self.BUS_NAME)
        except:
            return False
        self.write_i2c_word_data(AntennaDeployerCommand.DISARM_ANTS)

    def enable(self):
        """
        Arms the ISIS Antenna Deployer
        """
        try:
            self.bus.open(self.BUS_NAME)
        except:
            return False
        # FIXME: if enable / disable are used to arm / disarm the deploy method shouldn't call arm rather it should call self.enable()
        self.write_i2c_word_data(AntennaDeployerCommand.ARM_ANTS)
