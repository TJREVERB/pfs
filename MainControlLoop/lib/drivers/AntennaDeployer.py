import time
from enum import Enum
from smbus2 import SMBus
from MainControlLoop.lib.devices import Device


class AntennaDeployerCommand(Enum):
    SYSTEM_RESET = 0xAA
    WATCHDOG_RESET= 0xCC
    ARM_ANTS=0xAD
    DISARM_ANTS= 0xAC
    DEPLOY_1=0xA1
    DEPLOY_2=0xA2
    DEPLOY_3=0xA3
    DEPLOY_4=0xA4
    AUTO_DEPLOY=0xA5
    DEPLOY_1_OVERRIDE=0xBA
    DEPLOY_2_OVERRIDE=0xBB
    DEPLOY_3_OVERRIDE=0xBC
    DEPLOY_4_OVERRIDE=0xBD
    CANCEL_DEPLOY=0xA9
    GET_TEMP=0xC0
    GET_STATUS=0xC3
    GET_UPTIME_SYS=0xC6
    GET_TELEMETRY=0xC7
    GET_COUNT_1=0xB0
    GET_COUNT_2=0xB1
    GET_COUNT_3=0xB2
    GET_COUNT_4=0xB3
    GET_UPTIME_1=0xB4
    GET_UPTIME_2=0xB5
    GET_UPTIME_3=0xB6
    GET_UPTIME_4=0xB7


class AntennaDeployer(Device):

    def __init__(self):
        super().__init__("antenna_deployer")
        self.bus = SMBus(1)
        self.primary_address = 0x31
        self.secondary_address = 0x32


    def write_i2c_word_data(self, command: AntennaDeployerCommand, data: int) -> bool:
        if type(command) != AntennaDeployerCommand:
            return False

        self.bus.write_i2c_word_data(self.primary_address, command.value, data)
        return True


    def read_i2c_word_data(self, command: AntennaDeployerCommand) -> bytes or None:
        if type(command) != AntennaDeployerCommand:
            return None

        bus.write_word_data(self.primary_address, command.value, 0x00)
        time.sleep(0.5)
        return bus.read_byte(self.primary_address)


    def deploy(self, register: AntennaDeployerRegister):
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
        self.write_i2c_word_data(AntennaDeployerCommand.ARM_ANTS)
