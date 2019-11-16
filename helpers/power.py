from enum import Enum


class Power(Enum):
    """
    Enumerate object that contains power thresholds for each power mode
    """
    STARTUP = 8.2
    NORMAL = 7.6
    EMERGENCY = 0
