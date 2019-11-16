from enum import Enum


class Mode(Enum):
    """
    Enumerate that represents Modes as integers
    """
    NORMAL = 0
    LOW_POWER = 1
    EMERGENCY = 2