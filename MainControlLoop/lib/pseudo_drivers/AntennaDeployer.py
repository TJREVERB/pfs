import time
import random
from enum import Enum

class AntennaDeployerReadCommand(Enum):
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


class AntennaDeployerWriteCommand(Enum):
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



class AntennaDeployer:
    def __init__(self):
        self.counts = [0, 0, 0, 0]
        self.start_times = [-1, -1, -1, -1]
        self.status = True
        self.data = {
            AntennaDeployerReadCommand.GET_COUNT_1: lambda : self.counts[0],
            AntennaDeployerReadCommand.GET_COUNT_2: lambda : self.counts[1],
            AntennaDeployerReadCommand.GET_COUNT_3: lambda : self.counts[2],
            AntennaDeployerReadCommand.GET_COUNT_4: lambda : self.counts[3],
            AntennaDeployerReadCommand.GET_UPTIME_1: lambda : self.get_uptime(0),
            AntennaDeployerReadCommand.GET_UPTIME_2: lambda : self.get_uptime(1),
            AntennaDeployerReadCommand.GET_UPTIME_3: lambda : self.get_uptime(2),
            AntennaDeployerReadCommand.GET_UPTIME_4: lambda : self.get_uptime(3),
            AntennaDeployerReadCommand.GET_TEMP: lambda : self.get_temp(),
            AntennaDeployerReadCommand.GET_STATUS: lambda : self.status
        }

        self.deploys = [AntennaDeployerWriteCommand.DEPLOY_1,
                        AntennaDeployerWriteCommand.DEPLOY_2,
                        AntennaDeployerWriteCommand.DEPLOY_3,
                        AntennaDeployerWriteCommand.DEPLOY_4]
        self.armed = False


    def get_temp(self):
        return random.random()


    def get_uptime(self, idx):
        if self.start_times[idx] == -1:
            return 0
        return time.time() - self.start_times[idx]


    def read(self, command: AntennaDeployerReadCommand) -> bytes or None:
        if not isinstance(command, AntennaDeployerReadCommand):
            return None
        
        return self.data[command]()
    

    # Returns True if the write command was successful otherwise False
    def write(self, command: AntennaDeployerWriteCommand) -> bool:
        if not isinstance(command, AntennaDeployerWriteCommand):
            return False
        
        if command == AntennaDeployerWriteCommand.ARM_ANTS:
            self.armed = True
            return True

        if command == AntennaDeployerWriteCommand.DISARM_ANTS:
            self.armed = False
            return True
        
        if command in self.deploys:
            idx = self.deploys.index(command)
            self.start_times[idx] = time.time()
            self.counts[idx] += 1
            return True
        
        return False

