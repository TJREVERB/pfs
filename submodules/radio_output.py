#!/usr/bin/env python3
from . import aprs as aprs_mod
from . import iridium as iridium_mod

default_radio: str = "APRS"
aprs = "aprs"
iridium = "iridium"


def send(message: str, radio=None):
    """Send a message back to the groundstation.  If radio is None, then send the message on the default radio."""
    if radio is None:
        radio = default_radio
    if radio == "aprs":
        aprs_mod.enqueue(message)
    if radio == "iridium":
        iridium_mod.enqueue(message)
