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
from functools import partial

if is_simulate('eps'):
    from submodules import eps_test as eps
else:
    from submodules import eps


def start():
    global state, bperiod
    state = None
    bperiod = 60

    t = ThreadHandler(target=partial(send_heartbeat), name="send_heartbeat")
    t.start()


def send_heartbeat():
    # Packet header
    while state == Mode.NORMAL:
        packet = "HK"
        gps_packet = gps.get_cache()[-1]
        # Time, mode, TLM rate
        f1 = struct.pack("f", time.time())
        f1 += bytes(core.get_state())
        f1 += bytes(bperiod)
        packet += base64.b64encode(f1)
        # GPS coords
        packet += base64.b64encode(struct.pack('fff',
                                               gps_packet['lat'], gps_packet['lon'], gps_packet['alt']))

        # Battery percentage as a 24-bit int
        battery_level = eps.get_battery_bus_volts()

        enc = struct.pack('I', int((2 ** 24 - 1) * battery_level))[:3]
        packet += base64.b64encode(enc)
        # Command stats
        enc = struct.pack('HHH', command_ingest.total_received, command_ingest.total_errors,
                          command_ingest.total_success)
        packet += base64.b64encode(enc)
        radio_output.send_immediate_raw(packet)
        time.sleep(bperiod)


def enter_normal_mode():
    global bperiod, state
    state = Mode.NORMAL
    bperiod = 60


def enter_low_power_mode():
    global bperiod, state
    state = Mode.LOW_POWER
    bperiod = 120


def enter_emergency_mode():
    global bperiod, state
    state = Mode.EMERGENCY
