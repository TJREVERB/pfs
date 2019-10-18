import time
import smbus
import yaml

from smbus2 import SMBusWrapper
from . import telemetry

class EPS():
    def __init__(self, config_path, ):