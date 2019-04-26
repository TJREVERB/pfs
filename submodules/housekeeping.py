"""
Collects data for housekeeping packets.
This is a special case; all other telemetry should be collected in telemetry.py
"""

import base64
import struct
import time

import core
from core import config
from helpers.helpers import is_simulate
from submodules import command_ingest
from submodules import eps
from submodules import gps
from submodules import radio_output

from helpers.threadhandler import ThreadHandler
from functools import partial


def start():
    t = ThreadHandler(target=partial(send_heartbeat), name="send_heartbeat")
    t.start()


# TODO: Need to know what needs to be done in normal, low power, and emergency modes.
def enter_normal_mode():
    """
    Enter normal power mode.
    """
    pass


def enter_low_power_mode():
    """
    Enter low power mode.
    """
    pass


def enter_emergency_mode():
    """
    Enter emergency power mode.
    """
    pass


def send_heartbeat():
    while True:
        # Packet header
        packet = "HK"
        # Time, mode, TLM rate
        f1 = struct.pack("f", time.time())
        f1 += bytes(core.mode)
        f1 += bytes(config['housekeeping']['beacon_interval'])
        packet += base64.b64encode(f1)
        # GPS coords
        packet += base64.b64encode(struct.pack('fff',
                                               gps.lat, gps.lon, gps.alt))

        # Battery percentage as a 24-bit int
        if not is_simulate("eps"):
            battery_level = eps.get_battery_level()
        else:
            battery_level = None

        enc = struct.pack('I', int((2 ** 24 - 1) * battery_level))[:3]
        packet += base64.b64encode(enc)
        # Command stats
        enc = struct.pack('HHH', command_ingest.total_received, command_ingest.total_errors,
                          command_ingest.total_success)
        packet += base64.b64encode(enc)
        radio_output.send_immediate_raw(packet)
        time.sleep(config['housekeeping']['beacon_interval'])
