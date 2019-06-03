"""
Collects data for housekeeping packets.
This is a special case; all other telemetry should be collected in telemetry.py
"""

import base64
import struct
import time

import core
from core.mode import Mode
from core.helpers import is_simulate
from submodules import command_ingest
from submodules import gps
from submodules import radio_output

from core.threadhandler import ThreadHandler
from core import config
from functools import partial

if is_simulate('eps'):
    from submodules import eps_test as eps
else:
    from submodules import eps


def start():
    t = ThreadHandler(target=partial(send_heartbeat), name="send_heartbeat")
    t.start()


def send_heartbeat():
    while True:
        # Packet header
        packet = "HK"
        # gps_packet = gps.get_cache()[-1]
        # Time, mode, TLM rate
        f1 = struct.pack("f", time.time())
        f1 += bytes(core.get_state())

        if core.get_state() == Mode.LOW_POWER:
            f1 += bytes(config['housekeeping']['low_power_period'])
        else:
            f1 += bytes(config['housekeeping']['beacon_period'])
        packet += base64.b64encode(f1)
        # GPS coords
        # packet += base64.b64encode(struct.pack('fff',
        #                                        gps_packet['lat'], gps_packet['lon'], gps_packet['alt']))

        # Battery percentage as a 24-bit int
        battery_level = eps.get_battery_bus_volts()

        enc = struct.pack('I', int((2 ** 24 - 1) * battery_level))[:3]
        packet += base64.b64encode(enc)
        # Command stats
        enc = struct.pack('HHH', command_ingest.total_received, command_ingest.total_errors,
                          command_ingest.total_success)
        packet += base64.b64encode(enc)
        radio_output.send_immediate_raw(packet)

        if core.get_state() == Mode.LOW_POWER:
            time.sleep(config['housekeeping']['low_power_period'])
        else:
            time.sleep(config['housekeeping']['beacon_period'])
