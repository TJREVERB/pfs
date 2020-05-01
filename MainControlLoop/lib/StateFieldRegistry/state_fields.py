from enum import Enum


class StateField(Enum):

    # DUMP / BEACON TELEMETRY
    TIME = 'TIME'
    IIDIODE_OUT = 'IIDIODE_OUT'
    VIDIODE_OUT = 'VIDIODE_OUT'
    VPCM12V = 'VPCM12V'
    VPCMBATV = 'VPCMBATV'
    VPCM5V = 'VPCM5V'
    VPCM3V3 = 'VPCM3V3'
    VBCR1 = 'VBCR1'
    VBCR2 = 'VBCR2'
    VBCR33 = 'VBCR33'
    VSW3 = 'VSW3'
    ISW3 = 'ISW3'
    VSW4 = 'VSW4'
    ISW4 = 'ISW4'
    VSW6 = 'VSW6'
    ISW6 = 'ISW6'
    VSW7 = 'VSW7'
    ISW7 = 'ISW7'
    VSW8 = 'VSW8'
    ISW8 = 'ISW8'
    TLM_TBRD_DB = 'TLM_TBRD_DB'
    PDM_3_STAT = "PDM_3_STAT"
    PDM_4_STAT = "PDM_4_STAT"
    PDM_6_STAT = "PDM_6_STAT"
    PDM_7_STAT = "PDM_7_STAT"
    PDM_8_STAT = "PDM_8_STAT"

    # ANTENNA DEPLOYER STATEFIELDS
    AD_TEMP = "AD_TEMP"
    AD_STATUS = "AD_STATUS"
    AD_COUNTS = "AD_COUNTS"
    AD_UPTIMES = "AD_UPTIMES"
    DEPLOY_ANTENNA = "DEPLOY_ANTENNA"

    # TIME INTERVALS
    APRS_BEACON_INTERVAL = 'APRS_BEACON_INTERVAL'
    IRIDIUM_BEACON_INTERVAL = 'IRIDIUM_BEACON_INTERVAL'

    # TIME RECORDINGS
    APRS_LAST_MESSAGE_TIME = 'APRS_LAST_MESSAGE_TIME'
    IRIDIUM_LAST_MESSAGE_TIME = 'IRIDIUM_LAST_MESSAGE_TIME'
    APRS_LAST_BEACON_TIME = 'APRS_LAST_BEACON_TIME'
    LAST_ARCHIVE_TIME = 'LAST_ARCHIVE_TIME'
    BOOT_TIME = 'BOOT_TIME'

    # SYSTEM INFO
    BOOT_WAIT_COMPLETE = "FIRST_BOOT"
    ANTENNA_DEPLOYED = "ANTENNA_DEPLOY"
    ANTENNA_DEPLOY_ATTEMPTED = "ANTENNA_DEPLOY_ATTEMPTED"


class ErrorFlag(Enum):
    ANTENNA_DEPLOYER_FAILURE = "ANTENNA_DEPLOYER_FAILURE"
    APRS_FAILURE = "APRS_FAILURE"
    EPS_FAILURE = "EPS_FAILURE"
    IRIDIUM_FAILURE = "IRIDIUM_FAILURE"


StateFieldTypeCheck = {
    # DUMP / BEACON TELEMETRY
    StateField.TIME: float,
    StateField.IIDIODE_OUT: float,
    StateField.VIDIODE_OUT: float,
    StateField.VPCM12V: float,
    StateField.VPCMBATV: float,
    StateField.VPCM5V: float,
    StateField.VPCM3V3: float,
    StateField.VBCR1: float,
    StateField.VBCR2: float,
    StateField.VBCR33: float,
    StateField.VSW3: float,
    StateField.ISW3: float,
    StateField.VSW4: float,
    StateField.ISW4: float,
    StateField.VSW6: float,
    StateField.ISW6: float,
    StateField.VSW7: float,
    StateField.ISW7: float,
    StateField.VSW8: float,
    StateField.ISW8: float,
    StateField.TLM_TBRD_DB: float,
    StateField.PDM_3_STAT: int,
    StateField.PDM_4_STAT: int,
    StateField.PDM_6_STAT: int,
    StateField.PDM_7_STAT: int,
    StateField.PDM_8_STAT: int,
    
    # ANTENNA DEPLOYER FIELDS
    StateField.AD_TEMP: float,
    StateField.AD_STATUS: bool,
    StateField.AD_COUNTS: list,
    StateField.AD_UPTIMES: list,
    StateField.DEPLOY_ANTENNA: bool,

    # INTERVALS
    StateField.APRS_BEACON_INTERVAL: int,
    StateField.IRIDIUM_BEACON_INTERVAL: int,

    # TIME RECORDINGS
    StateField.APRS_LAST_MESSAGE_TIME: float,
    StateField.IRIDIUM_LAST_MESSAGE_TIME: float,
    StateField.APRS_LAST_BEACON_TIME: float,
    StateField.LAST_ARCHIVE_TIME: float,
    StateField.BOOT_TIME: float,

    # SYSTEM INFO
    StateField.BOOT_WAIT_COMPLETE: bool,
    StateField.ANTENNA_DEPLOYED: bool,
    StateField.ANTENNA_DEPLOY_ATTEMPTED: bool
}

for state_field in StateField:
    if state_field not in StateFieldTypeCheck:
        raise NotImplementedError(f"{state_field}'s type has not been declared in StateFieldTypeCheck dictionary.")
