from enum import Enum
import time

from MainControlLoop.lib.devices import Device
from MainControlLoop.lib.StateFieldRegistry.state_fields import ErrorFlag

from smbus2 import SMBus

# TODO: If repeated failures found (refer to registry.py and state_fields.py), raise ErrorFlag to invoke a device reset
# TODO: Write read_task based off APRS/read_task in tasks, call raise_error method if error in read_task
# TODO: Add None checking for DATA_ZERO values
# TODO: Ensure manual reset works, especially since it can't pass type checking at the moment
# NOTE: Currently getting ACTUAL_PIN_STATUS doesn't work, probably a similar problem to reading data from solar panels

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
    """
    These addresses refer to the last argument (normally referred to as the "data" argument), usually when data is
    requested via the get telemetry command (a register value of 0x10). Note that self.get_formatted_bytes() should
    almost always be called with an EPSAddress as the argument when using smbus2 reading or writing calls.
    """
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
    """
    The hex addresses of PDM pins on the EPS are pretty simple and direct, i.e. PDM1 = 0x01, PDM2 = 0x02, etc.
    """
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
    bus = SMBus(1)
    BUS_NAME = '/dev/i2c-1'
    ADDRESS = 0x2b
    DEFAULT_READ_DELAY = 500
    DEFAULT_RETURN_LENGTH = 2
    # Number of expected return bytes.
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
    # Expected read/write delay of commands. Those without a WR_DELAY in documentation have been assigned to zero.
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
    # Commonly the "data" (last) argument in smbus2 methods (the Data[0] column in ClydeSpace documentation), returns
    # a None for modifying methods or methods that require a specific Pin number (e.g. PDM_N methods and GET_TELEMETRY)
    DATA_ZERO = {
        EPSRegister.BOARD_STATUS: 0x00,
        EPSRegister.GET_LAST_ERROR: 0x00,
        EPSRegister.GET_VERSION: 0x00,
        EPSRegister.GET_CHECKSUM: 0x00,
        EPSRegister.GET_REVISION: 0x00,
        EPSRegister.GET_TELEMETRY: None,
        EPSRegister.GET_COMMS_WATCHDOG_PERIOD: 0x00,
        EPSRegister.SET_COMMS_WATCHDOG_PERIOD: None,
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
        EPSRegister.SWITCH_PDM_N_ON: None,
        EPSRegister.SWITCH_PDM_N_OFF: None,
        EPSRegister.SET_PDM_N_INITIAL_STATE_TO_ON: None,
        EPSRegister.SET_PDM_N_INITIAL_STATE_TO_OFF: None,
        EPSRegister.GET_PDM_N_ACTUAL_STATUS: None,
        EPSRegister.SET_PDM_N_TIMER_LIMIT: None,
        EPSRegister.GET_PDM_N_TIMER_LIMIT: None,
        EPSRegister.GET_PDM_N_CURRENT_TIMER_VALUE: None,
        EPSRegister.PCM_RESET: None,
        EPSRegister.MANUAL_RESET: 0x00
    }
    # Mapping main Cubesat devices and components to their assigned PDM pin values.
    COMPONENT_TO_PIN = {
        "IRIDIUM": EPSPin.PDM3,
        "SATT4": EPSPin.PDM4,
        "ANTENNA_DEPLOYER": EPSPin.PDM5,
        "USB_TO_UART": EPSPin.PDM6,
        "MAX3232": EPSPin.PDM6
    }

    def __init__(self):
        super().__init__("EPS")

    def get_formatted_bytes(self, command: int) -> bool or list:
        # TESTED AND CONFIRMED WORKING
        if type(command) != int:
            return False
        if command > 0xFF:
            prefix = command >> 8
            suffix = command & 0XFF
            return [prefix, suffix]
        else:
            return [command]

    # For reference: data arguments can be an EPSAddress (for telemetry), EPSPin (for modifying specific pins), or
    # EPSRegister (for referencing DATA_ZERO, e.g. MANUAL_RESET or other system-wide setters).
    def read_write_with_delay(self, register: EPSRegister, data: EPSAddress or EPSPin or EPSRegister, delay: int = DEFAULT_READ_DELAY) -> bool or list:
        # TESTED AND CONFIRMED WORKING IN PREVIOUS VERSION
        if type(register) != EPSRegister or (type(data) != EPSAddress and type(data) != EPSPin and type(data) != EPSRegister) or type(delay) != int:
            return False
        try:
            if not self.write_i2c_block_data(register, data):
                return False
            delay = delay / 1000  # Since in milliseconds, need to convert to seconds for time.sleep()
            try:
                assert delay < 1.0  # No WR_DELAY is longer than one second
            except AssertionError:
                return False
            time.sleep(delay)  # Potentially dangerous as it may freeze up MCL?
            data_returned = self.read_i2c_block_data(register, self.EXPECTED_RETURN_BYTES[register])
            if type(data_returned) == bool and data_returned is False:
                return False
            return data_returned
        except:
            return False

    def write_i2c_block_data(self, register: EPSRegister, data: EPSAddress or EPSPin or EPSRegister) -> bool:
        # Not unit tested, although has been implicitly checked through read_data_with_delay
        if type(register) != EPSRegister or (type(data) != EPSPin and type(data) != EPSAddress and type(data) != EPSRegister):
            return False
        try:
            command = self.get_formatted_bytes(data.value)
            self.bus.write_i2c_block_data(self.ADDRESS, register.value, command)
            return True
        except:
            return False

    def read_i2c_block_data(self, register: EPSRegister, length: int = DEFAULT_RETURN_LENGTH) -> bool or list:
        # Not unit tested, although has been implicitly checked through read_data_with_delay
        if type(register) != EPSRegister or type(length) != int:
            return False
        if length != self.EXPECTED_RETURN_BYTES[register]:
            return False
        try:
            data = self.bus.read_i2c_block_data(self.ADDRESS, register.value, length)
            return data
        except:
            return False

    # The following methods are implemented wrappers for common commands:
    def pin_on(self, pin: EPSPin) -> bool:
        # TESTED AND CONFIRMED WORKING
        if type(pin) != EPSPin:
            return False
        try:
            if not self.write_i2c_block_data(EPSRegister.SWITCH_PDM_N_ON, pin):
                return False
            time.sleep(self.WR_DELAY[EPSRegister.SWITCH_PDM_N_ON])
            data_returned = self.read_write_with_delay(EPSRegister.GET_PDM_N_ACTUAL_STATUS, pin, self.WR_DELAY[EPSRegister.GET_PDM_N_ACTUAL_STATUS])
            if type(data_returned) == bool and data_returned is False:
                return False
            return True
        except:
            return False

    # The following methods have not been tested at all:
    def pin_off(self, pin: EPSPin) -> bool:
        if type(pin) != EPSPin:
            return False
        try:
            if not self.write_i2c_block_data(EPSRegister.SWITCH_PDM_N_OFF, pin):
                return False
            time.sleep(self.WR_DELAY[EPSRegister.SWITCH_PDM_N_OFF])
            data_returned = self.read_write_with_delay(EPSRegister.GET_PDM_N_ACTUAL_STATUS, pin, self.WR_DELAY[EPSRegister.GET_PDM_N_ACTUAL_STATUS])
            if type(data_returned) == bool and data_returned is False:
                return False
            return True
        except:
            return False

    def set_all_PDMS_to_inital_state(self) -> bool:
        data_returned = self.read_write_with_delay(EPSRegister.SET_ALL_PDMS_TO_INITIAL_STATE, self.DATA_ZERO[EPSRegister.SET_ALL_PDMS_TO_INITIAL_STATE], self.WR_DELAY[EPSRegister.SET_ALL_PDMS_TO_INITIAL_STATE])
        if type(data_returned) == bool and data_returned is False:
            return False
        return True

    def reset_comms_watchdog(self) -> bool:
        data_returned = self.read_write_with_delay(EPSRegister.RESET_COMMS_WATCHDOG, self.DATA_ZERO[EPSRegister.RESET_COMMS_WATCHDOG], self.WR_DELAY[EPSRegister.RESET_COMMS_WATCHDOG])
        if type(data_returned) == bool and data_returned is False:
            return False
        return True

    def functional(self) -> bool:
        data_returned = self.read_write_with_delay(EPSRegister.BOARD_STATUS, self.DATA_ZERO[EPSRegister.BOARD_STATUS], self.WR_DELAY[EPSRegister.BOARD_STATUS])
        if type(data_returned) == bool and data_returned is False:
            return False
        # Ambiguity: both an error and an inoperable board return False, although practically these mean the same thing
        if data_returned[0] == 1:  # Need to research what the BOARD_STATUS command actually returns
            return True
        return False

    def reset(self) -> bool:
        if not self.write_i2c_block_data(EPSRegister.MANUAL_RESET, EPSRegister.MANUAL_RESET):
            return False
        return True

    def disable(self) -> bool:  # Are these inherited methods from Device? We should probably never disable the EPS
        raise NotImplementedError

    def enable(self) -> bool:
        raise NotImplementedError
