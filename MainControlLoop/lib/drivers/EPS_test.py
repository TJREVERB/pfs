from enum import Enum
import time

# from MainControlLoop.lib.devices import Device
# from MainControlLoop.lib.StateFieldRegistry.state_fields import ErrorFlag

from smbus2 import SMBus, SMBusWrapper


class EPSRegister(Enum):
    """
    These correlate with the "Command" hex values column on Table 11.2 of Clyde Space documnetation. They
    are used in the "register" argument for any standard I2C commands using smbus or smbus2, e.g.
    the second argument in read_i2c_block_data or write_i2c_block_data. Note that any PDM methods will
    specify "PDM_N" or "ALL_PDMS" to indicate whether a method is for a specific PDM or all (respectively).
    """
    BOARD_STATUS = 0x01
    GET_LAST_ERROR = 0x03
    GET_VERSION = 0x04
    GET_CHECKSUM = 0x05
    GET_REVISION = 0x06
    GET_TELEMETRY = 0x10
    GET_COMMS_WATCHDOG_PERIOD = 0x20
    SET_COMMS_WATCHDOG_PERIOD = 0x21
    RESET_COMMS_WATCHDOG = 0x22
    GET_BROWN_OUT_RESETS = 0x31
    GET_AUTO_SOFTWARE_RESETS = 0x32
    GET_MANUAL_RESETS = 0x33
    GET_COMMS_WATCHDOG_RESETS = 0x34
    SWITCH_ON_ALL_PDMS = 0x40
    SWITCH_OFF_ALL_PDMS = 0x41
    GET_ACTUAL_STATE_ALL_PDMS = 0x42
    GET_EXPECTED_STATE_ALL_PDMS = 0X43
    GET_INITIAL_STATE_ALL_PDMS = 0X44
    SET_ALL_PDMS_TO_INITIAL_STATE = 0X45
    SWITCH_PDM_N_ON = 0X50
    SWITCH_PDM_N_OFF = 0X51
    SET_PDM_N_INITIAL_STATE_TO_ON = 0x52
    SET_PDM_N_INITIAL_STATE_TO_OFF = 0x53
    GET_PDM_N_ACTUAL_STATUS = 0X54
    SET_PDM_N_TIMER_LIMIT = 0X60
    GET_PDM_N_TIMER_LIMIT = 0X61
    GET_PDM_N_CURRENT_TIMER_VALUE = 0X62
    PCM_RESET = 0X70
    MANUAL_RESET = 0X80
    PDM_STATUS = 0x0E

class EPSAddress(Enum):
    IIDIODE_OUT = 0xE284
    VIDIODE_OUT = 0xE280
    I3V3_DRW = 0xE205
    I5V_DRW = 0xE215
    IPCM12V = 0xE234
    VPCM12V = 0xE230
    IPCMBATV = 0xE224
    VPCMBATV = 0xE220
    IPCM5V = 0xE214
    VPCM5V = 0xE210
    IPCM3V3 = 0xE204
    VPCM3V3 = 0xE200

    VSW1 = 0xE410
    ISW1 = 0xE414
    VSW2 = 0xE420
    ISW2 = 0xE424
    VSW3 = 0xE430
    ISW3 = 0xE434
    VSW4 = 0xE440
    ISW4 = 0xE444
    VSW5 = 0xE450
    ISW5 = 0xE454
    VSW6 = 0xE460
    ISW6 = 0xE464
    VSW7 = 0xE470
    ISW7 = 0xE474
    VSW8 = 0xE480
    ISW8 = 0xE484
    VSW9 = 0xE490
    ISW9 = 0xE494
    VSW10 = 0xE4A0
    ISW10 = 0xE4A4

    VBCR1 = 0xE110
    IBCR1A = 0xE114
    IBCR1B = 0xE115
    TBCR1A = 0xE118
    TBCR1B = 0xE119
    SDBCR1A = 0xE11C
    SDBCR1B = 0xE11D
    VBCR2 = 0xE120
    IBCR2A = 0xE124
    IBCR2B = 0xE125
    TBCR2A = 0xE128
    TBCR2B = 0xE129
    SDBCR2A = 0xE12C
    SDBCR2B = 0xE12D
    VBCR33 = 0xE130
    IBCR3A4 = 0xE134
    IBCR3B = 0xE135
    TBCR3A = 0xE138
    TBCR3B = 0xE139
    SDBCR3A = 0xE13C
    SDBCR3B = 0xE13D

class EPSPin(Enum):
    PDM1 = 0x01
    PDM2 = 0x02
    PDM3 = 0x03
    PDM4 = 0x04
    PDM5 = 0x05
    PDM6 = 0x06
    PDM7 = 0x07
    PDM8 = 0x08
    PDM9 = 0x09
    PDM10 = 0x10

class EPS():
    # TODO: Add write and read, where there is a built-in sleep, add default sleep argument
    # TODO: Try-catches in each wrapper
    # TODO: Writing a script to determine the direction of current flow
    bus = SMBus(1)
    BUS_NAME = '/dev/i2c-1'
    ADDRESS = 0x2b
    DEFAULT_READ_DELAY = 0.5
    DEFAULT_RETURN_LENGTH = 2
    # Number of expected return bytes
    EXPECTED_RETURN_BYTES = {
        EPSRegister.BOARD_STATUS: 2,
        EPSRegister.GET_LAST_ERROR: 2,
        EPSRegister.GET_VERSION: 2,
        EPSRegister.GET_CHECKSUM: 2,
        EPSRegister.GET_REVISION: 2,
        EPSRegister.GET_TELEMETRY: 2,
        EPSRegister.GET_COMMS_WATCHDOG_PERIOD: 2,
        EPSRegister.SET_COMMS_WATCHDOG_PERIOD: 0,
        EPSRegister.RESET_COMMS_WATCHDOG: 0,
        EPSRegister.GET_BROWN_OUT_RESETS: 2,
        EPSRegister.GET_AUTO_SOFTWARE_RESETS: 2,
        EPSRegister.GET_MANUAL_RESETS: 2,
        EPSRegister.GET_COMMS_WATCHDOG_RESETS: 2,
        EPSRegister.SWITCH_ON_ALL_PDMS: 0,
        EPSRegister.SWITCH_OFF_ALL_PDMS: 0,
        EPSRegister.GET_ACTUAL_STATE_ALL_PDMS: 4,
        EPSRegister.GET_EXPECTED_STATE_ALL_PDMS: 4,
        EPSRegister.GET_INITIAL_STATE_ALL_PDMS: 4,
        EPSRegister.SET_ALL_PDMS_TO_INITIAL_STATE: 4,
        EPSRegister.SWITCH_PDM_N_ON: 0,
        EPSRegister.SWITCH_PDM_N_OFF: 0,
        EPSRegister.SET_PDM_N_INITIAL_STATE_TO_ON: 0,
        EPSRegister.SET_PDM_N_INITIAL_STATE_TO_OFF: 0,
        EPSRegister.GET_PDM_N_ACTUAL_STATUS: 2,
        EPSRegister.SET_PDM_N_TIMER_LIMIT: 0,
        EPSRegister.GET_PDM_N_TIMER_LIMIT: 0,
        EPSRegister.GET_PDM_N_CURRENT_TIMER_VALUE: 0,
        EPSRegister.PCM_RESET: 0,
        EPSRegister.MANUAL_RESET: 0
    }
    # Expected read/write delay
    WR_DELAY = {
        EPSRegister.BOARD_STATUS: 1,
        EPSRegister.GET_LAST_ERROR: 1,
        EPSRegister.GET_VERSION: 1,
        EPSRegister.GET_CHECKSUM: 35,
        EPSRegister.GET_REVISION: 1,
        EPSRegister.GET_TELEMETRY: 5,
        EPSRegister.GET_COMMS_WATCHDOG_PERIOD: 1,
        EPSRegister.SET_COMMS_WATCHDOG_PERIOD: 0,
        EPSRegister.RESET_COMMS_WATCHDOG: 0,
        EPSRegister.GET_BROWN_OUT_RESETS: 1,
        EPSRegister.GET_AUTO_SOFTWARE_RESETS: 1,
        EPSRegister.GET_MANUAL_RESETS: 1,
        EPSRegister.GET_COMMS_WATCHDOG_RESETS: 1,
        EPSRegister.SWITCH_ON_ALL_PDMS: 0,
        EPSRegister.SWITCH_OFF_ALL_PDMS: 0,
        EPSRegister.GET_ACTUAL_STATE_ALL_PDMS: 20,
        EPSRegister.GET_EXPECTED_STATE_ALL_PDMS: 1,
        EPSRegister.GET_INITIAL_STATE_ALL_PDMS: 20,
        EPSRegister.SET_ALL_PDMS_TO_INITIAL_STATE: 20,
        EPSRegister.SWITCH_PDM_N_ON: 0,
        EPSRegister.SWITCH_PDM_N_OFF: 0,
        EPSRegister.SET_PDM_N_INITIAL_STATE_TO_ON: 200,
        EPSRegister.SET_PDM_N_INITIAL_STATE_TO_OFF: 200,
        EPSRegister.GET_PDM_N_ACTUAL_STATUS: 2,
        EPSRegister.SET_PDM_N_TIMER_LIMIT: 200,
        EPSRegister.GET_PDM_N_TIMER_LIMIT: 5,
        EPSRegister.GET_PDM_N_CURRENT_TIMER_VALUE: 1,
        EPSRegister.PCM_RESET: 1,
        EPSRegister.MANUAL_RESET: 0

    }
    # First argument (data[0])
    DATA_ZERO = {
        EPSRegister.BOARD_STATUS: 0x00,
        EPSRegister.GET_LAST_ERROR: 0x00,
        EPSRegister.GET_VERSION: 0x00,
        EPSRegister.GET_CHECKSUM: 0x00,
        EPSRegister.GET_REVISION: 0x00,
        ######################
        EPSRegister.GET_TELEMETRY: 11-8,
        ######################
        EPSRegister.GET_COMMS_WATCHDOG_PERIOD: 0x00,
        #####################
        EPSRegister.SET_COMMS_WATCHDOG_PERIOD: 10,
        ######################
        EPSRegister.RESET_COMMS_WATCHDOG: 0x00,
        EPSRegister.GET_BROWN_OUT_RESETS: 0x00,
        EPSRegister.GET_AUTO_SOFTWARE_RESETS: 0x00,
        EPSRegister.GET_MANUAL_RESETS: 0x00,
        EPSRegister.GET_COMMS_WATCHDOG_RESETS: 0x00,
        EPSRegister.SWITCH_ON_ALL_PDMS: 0x00,
        EPSRegister.SWITCH_OFF_ALL_PDMS: 0x00,
        EPSRegister.GET_ACTUAL_STATE_ALL_PDMS: 0x00,
        EPSRegister.GET_EXPECTED_STATE_ALL_PDMS: 0x00,
        EPSRegister.GET_INITIAL_STATE_ALL_PDMS: 0x00,
        EPSRegister.SET_ALL_PDMS_TO_INITIAL_STATE: 0x00,
        ######################
        EPSRegister.SWITCH_PDM_N_ON: 10,
        EPSRegister.SWITCH_PDM_N_OFF: 10,
        EPSRegister.SET_PDM_N_INITIAL_STATE_TO_ON: 10,
        EPSRegister.SET_PDM_N_INITIAL_STATE_TO_OFF: 10,
        EPSRegister.GET_PDM_N_ACTUAL_STATUS: 10,
        EPSRegister.SET_PDM_N_TIMER_LIMIT: 10,
        EPSRegister.GET_PDM_N_TIMER_LIMIT: 10,
        EPSRegister.GET_PDM_N_CURRENT_TIMER_VALUE: 10,
        EPSRegister.PCM_RESET: 11-14,
        #######################
        EPSRegister.MANUAL_RESET: 0x00
    }

    COMPONENT_TO_PIN = {
        "IRIDIUM": EPSPin.PDM3,
        "SATT4": EPSPin.PDM4,
        "ANTENNA_DEPLOYER": EPSPin.PDM5,
        "USB_TO_UART": EPSPin.PDM6,
        "MAX3232": EPSPin.PDM6
    }

    # def __init__(self):
    #     super().__init__("EPS")

    def get_formatted_bytes(self, command: int) -> bool or list:
        # This method as been tested and confirmed working
        if type(command) != int:
            return False
            # return ErrorFlag.EPS_TYPE_FAILURE
        if command > 0xFF:
            prefix = command >> 8
            suffix = command & 0XFF
            return [prefix, suffix]
        else:
            return [command]

    def read_data_with_delay(self, register: EPSRegister, data: EPSAddress or EPSPin, delay: int = DEFAULT_READ_DELAY) -> bool or list:
        # TODO: Write a command, wait for confirmation, then request for a read
        if type(register) != EPSRegister or (type(data) != EPSAddress and type(data) != EPSPin) or type(delay) != int:
            print("readdelaytypecheck")
            return False
        try:
            if not self.write_i2c_block_data(register, data):
                print("readdelaywriteerror")
                return False
            time.sleep(delay)  # Potentially dangerous
            data_returned = self.read_i2c_block_data(register, self.EXPECTED_RETURN_BYTES[register])
            if type(data_returned) == bool and data_returned is False:
                return False
            return data_returned
        except:
            return False

    def write_i2c_block_data(self, register: EPSRegister, data: EPSAddress or EPSPin) -> bool:
        if type(register) != EPSRegister or (type(data) != EPSPin and type(data) != EPSAddress):
            print("writetypecheck")
            return False
            # return ErrorFlag.EPS_TYPE_FAILURE
        try:
            command = self.get_formatted_bytes(data.value)
            self.bus.write_i2c_block_data(self.ADDRESS, register.value, command)
            return True
        except:
            print("writeerror")
            return False
            # return ErrorFlag.EPS_I2C_FAILURE

    def read_i2c_block_data(self, register: EPSRegister, length: int = DEFAULT_RETURN_LENGTH) -> bool or list:
        if type(register) != EPSRegister or type(length) != int:
            return False
            # return ErrorFlag.EPS_TYPE_FAILURE
        if length != self.EXPECTED_RETURN_BYTES[register]:
            return False
        try:
            data = self.bus.read_i2c_block_data(self.ADDRESS, register.value, length)
            return data
        except:
            # TODO: Write specific error catching from registry.py and state_fields.py
            # TODO: Base read_task off APRS/read_task in tasks
            return False
    # TODO: The following methods are implemented wrappers for common commands.
    # TODO: Call raise_error method if error in read_task
    # The following methods are implemented wrappers for common commands:

    def pin_on(self, pin: EPSPin) -> bool:
        if type(pin) != EPSPin:
            return False
        try:
            if not self.write_i2c_block_data(EPSRegister.SWITCH_PDM_N_ON, pin):
                print("overallwriteerror")
                return False
            time.sleep(self.WR_DELAY[EPSRegister.SWITCH_PDM_N_ON])
            data_returned = self.read_data_with_delay(EPSRegister.GET_PDM_N_ACTUAL_STATUS, pin, self.WR_DELAY[EPSRegister.GET_PDM_N_ACTUAL_STATUS])
            if type(data_returned) == bool and data_returned is False:
                return False
            print(data_returned)
            return True
        except:
            return False

    def functional(self):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def disable(self):
        raise NotImplementedError

    def enable(self):
        raise NotImplementedError