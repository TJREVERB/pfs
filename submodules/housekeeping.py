# Collects data for housekeeping packets
import base64
import struct
import threading
import time

import core
from core import config
from . import command_ingest
from . import radio_output
from . import eps
from . import gps


def on_startup():
    t = threading.Thread(target=send_heartbeat, daemon=True)
    t.start()


def enter_normal_mode():
    pass


def enter_low_power_mode():
    pass


def enter_emergency_mode():
    pass


def send_heartbeat():
    while True:
        # Packet header
        packet = "TJHK"
        # Time, mode, TLM rate
        f1 = struct.pack("f", time.time())
        f1 += bytes(core.current_mode)
        f1 += bytes(config['housekeeping']['beacon_interval'])
        packet += base64.b64encode(f1)
        # GPS coords
        packet += base64.b64encode(struct.pack('fff', gps.lat, gps.lon, gps.alt))
        # Battery percentage... as a 24 bit int :(
        battery_level = eps.get_battery_level()
        enc = struct.pack('I', int((2 ** 24 - 1) * battery_level))[:3]
        packet += base64.b64encode(enc)
        # Command stats
        enc = struct.pack('HHH', command_ingest.total_recieved, command_ingest.total_errors,
                          command_ingest.total_success)
        packet += base64.b64encode(enc)
        radio_output.send(packet)
        time.sleep(config['housekeeping']['beacon_interval'])
