from enum import Enum


# TODO: decide if the Mode enum should be the same across all control tasks (benefit: simplicity, cons: less control over each module)

class Mode(Enum):
    NORMAL = "NORMAL"
    LOW_POWER = "LOW_POWER"
    SAFE = "SAFE"
    COMMS = "COMMS"
    BOOT = "BOOT"
    STARTUP = "STARTUP"
