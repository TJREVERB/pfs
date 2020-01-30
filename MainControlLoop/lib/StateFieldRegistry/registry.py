from copy import deepcopy

from .state_fields import StateField, ErrorFlag, StateFieldTypeCheck


class StateFieldRegistry:

    def __init__(self):
        """
        Defines all the StateFields present in the state registry
        """
        self.registry = {
            StateField.EPS_BATTERY_VOLTAGE: 0,
            StateField.SYS_TIME: 0.0,
            StateField.APRS_BEACON_INTERVAL: 0,
            StateField.IRIDIUM_BEACON_INTERVAL: 0,
            StateField.APRS_LAST_MESSAGE_TIME: 0,
            StateField.IRIDIUM_LAST_MESSAGE_TIME: 0,
        }

        self.hardware_faults = {
            ErrorFlag.ANTENNA_DEPLOYER_FAILURE: False,
            ErrorFlag.APRS_FAILURE: False,
            ErrorFlag.EPS_FAILURE: False,
            ErrorFlag.IRIDIUM_FAILURE: False
        }

    def update(self, field: StateField, value):
        """
        Update a StateField in the registry.
        :param field: (StateField) StateField type to update in registry
        :param value: (Any) Value to put in the registry,
        :return: (bool) If the value was updated in the registry
        """
        if field not in self.registry:
            return False

        required_type = StateFieldTypeCheck[field]
        if type(value) != required_type:
            return False

        self.registry[field] = value

        return True

    def get(self, field: StateField):
        """
        Returns a StateField from the registry
        :param field: (StateField) StateField type to get from registry
        :return: (Any) The value found in the registry.
        """
        if field in self.registry:
            return deepcopy(self.registry[field])

        return None

    def raise_flag(self, flag: ErrorFlag):
        if flag in self.hardware_faults:
            self.hardware_faults[flag] = True

    def drop_flag(self, flag: ErrorFlag):
        if flag in self.hardware_faults:
            self.hardware_faults[flag] = False


