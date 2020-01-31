from enum import Enum


class StateField(Enum):
    EPS_BATTERY_VOLTAGE = 'EPS_BATTERY_VOLTAGE'
    SYS_TIME = 'SYS_TIME'
    APRS_BEACON_INTERVAL = 'APRS_BEACON_INTERVAL'
    IRIDIUM_BEACON_INTERVAL = 'IRIDIUM_BEACON_INTERVAL'
    APRS_LAST_MESSAGE_TIME = 'APRS_LAST_MESSAGE_TIME'
    IRIDIUM_LAST_MESSAGE_TIME = 'IRIDIUM_LAST_MESSAGE_TIME'
    APRS_LAST_BEACON_TIME = 'APRS_LAST_BEACON_TIME'


class ErrorFlag(Enum):
    ANTENNA_DEPLOYER_FAILURE = "ANTENNA_DEPLOYER_FAILURE"
    APRS_FAILURE = "APRS_FAILURE"
    EPS_FAILURE = "EPS_FAILURE"
    IRIDIUM_FAILURE = "IRIDIUM_FAILURE"


StateFieldTypeCheck = {
    StateField.EPS_BATTERY_VOLTAGE: float,
    StateField.SYS_TIME: float,
    StateField.APRS_BEACON_INTERVAL: int,
    StateField.IRIDIUM_BEACON_INTERVAL: int,
    StateField.APRS_LAST_MESSAGE_TIME: float,
    StateField.IRIDIUM_LAST_MESSAGE_TIME: float,
    StateField.APRS_LAST_BEACON_TIME: float,
}

for state_field in StateField:
    if state_field not in StateFieldTypeCheck:
        raise NotImplementedError(f"{state_field}'s type has not been declared in StateFieldTypeCheck dictionary.")
