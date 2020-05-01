from copy import deepcopy

from .state_fields import StateField, ErrorFlag, StateFieldTypeCheck


class StateFieldRegistry:

    def __init__(self):
        """
        Defines all the StateFields present in the state registry
        """
        self.registry = {
            # DUMP / BEACON TELEMETRY
            StateField.TIME: 0.0,
            StateField.IIDIODE_OUT: 0.0,
            StateField.VIDIODE_OUT: 0.0,
            StateField.VPCM12V: 0.0,
            StateField.VPCMBATV: 0.0,
            StateField.VPCM5V: 0.0,
            StateField.VPCM3V3: 0.0,
            StateField.VBCR1: 0.0,
            StateField.VBCR2: 0.0,
            StateField.VBCR33: 0.0,
            StateField.VSW3: 0.0,
            StateField.ISW3: 0.0,
            StateField.VSW4: 0.0,
            StateField.ISW4: 0.0,
            StateField.VSW6: 0.0,
            StateField.ISW6: 0.0,
            StateField.VSW7: 0.0,
            StateField.ISW7: 0.0,
            StateField.VSW8: 0.0,
            StateField.ISW8: 0.0,
            StateField.TLM_TBRD_DB: 0.0,
            StateField.PDM_3_STAT: -1,
            StateField.PDM_4_STAT: -1,
            StateField.PDM_6_STAT: -1,
            StateField.PDM_7_STAT: -1,
            StateField.PDM_8_STAT: -1,

            # ANTENNA DEPLOYER FIELDS
            StateField.AD_TEMP: 0.0,
            StateField.AD_STATUS: False,
            StateField.AD_COUNTS: [0, 0, 0, 0],
            StateField.AD_UPTIMES: [0, 0, 0, 0],
            StateField.DEPLOY_ANTENNA: False,

            # INTERVALS
            StateField.APRS_BEACON_INTERVAL: -1,
            StateField.IRIDIUM_BEACON_INTERVAL: -1,

            # TIME RECORDINGS
            StateField.APRS_LAST_MESSAGE_TIME: 0.0,
            StateField.IRIDIUM_LAST_MESSAGE_TIME: 0.0,
            StateField.APRS_LAST_BEACON_TIME: 0.0,
            StateField.LAST_ARCHIVE_TIME: 0.0,
            StateField.BOOT_TIME: -1,

            # SYSTEM INFO
            StateField.BOOT_WAIT_COMPLETE: False,
            StateField.ANTENNA_DEPLOYED: False,
            StateField.ANTENNA_DEPLOY_ATTEMPTED: False
        }

        self.hardware_faults = {
            ErrorFlag.ANTENNA_DEPLOYER_FAILURE: False,
            ErrorFlag.APRS_FAILURE: False,
            ErrorFlag.EPS_FAILURE: False,
            ErrorFlag.IRIDIUM_FAILURE: False
        }


    #TODO: Remove Exceptions when uploading final version
    def update(self, field: StateField, value):
        """
        Update a StateField in the registry.
        :param field: (StateField) StateField type to update in registry
        :param value: (Any) Value to put in the registry,
        :return: (bool) If the value was updated in the registry
        """
        if field not in self.registry:
            raise Exception("Field not in registry")
            return False

        required_type = StateFieldTypeCheck[field]
        if type(value) != required_type:
            raise Exception("Field not of required type")
            return False

        self.registry[field] = value

        return True


    #TODO: Remove Exceptions when uploading final version
    def get(self, field: StateField):
        """
        Returns a StateField from the registry
        :param field: (StateField) StateField type to get from registry
        :return: (Any) The value found in the registry.
        """
        if field in self.registry:
            return deepcopy(self.registry[field])

        raise Exception("Field not found")
        return None


    #TODO: Remove Exceptions when uploading final version
    def raise_flag(self, flag: ErrorFlag):
        if flag in self.hardware_faults:
            self.hardware_faults[flag] = True
            return
        raise Exception("Flag not found")


    #TODO: Remove Exceptions when uploading final version
    def drop_flag(self, flag: ErrorFlag):
        if flag in self.hardware_faults:
            self.hardware_faults[flag] = False
            return
        raise Exception("Flag not found")


    def critical_failure(self):
        return self.hardware_faults[ErrorFlag.APRS_FAILURE] or self.hardware_faults[ErrorFlag.EPS_FAILURE] or self.hardware_faults[ErrorFlag.ANTENNA_DEPLOYER_FAILURE]
