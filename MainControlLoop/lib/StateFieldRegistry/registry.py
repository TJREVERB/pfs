from typing import Type

from .state_fields import StateField


class StateFieldRegistry:
    TYPE_CHECK = {
        StateField.EPS_BATTERY_VOLTAGE: float,
    }

    def __init__(self):
        """
        Defines all the StateFields present in the state registry
        """
        self.registry = {
            StateField.EPS_BATTERY_VOLTAGE: 9,
        }

    def add(self, field: StateField, value):
        """
        Add a StateField to the registry.
        :param field: (StateField) StateField type to add in registry
        :param value: (Any) Value to add to the registry,
        :return: (bool) If the value was added to the registry
        """
        if field not in self.registry:
            return False

        required_type = self.TYPE_CHECK[field]
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
            return self.registry[field]
        return None



