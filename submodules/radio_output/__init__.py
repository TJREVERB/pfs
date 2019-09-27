from threading import Lock
from time import sleep

from submodules import aprs
from submodules import iridium
from core import get_config

"""
send_lock is a threading lock that only allows one process to access a resource
"""
send_lock = Lock() # Instance of threading lock

"""
Send a message back to the groundstation.
:param message: Message to send to the radio.
:param radio: Radio to which to send the message. If `None`, send to the default radio.
"""


def send(message: str, radio="aprs"):
    with send_lock: # When a process tries to access this method, it must receive the lock before continuing
        if radio == "iridium":
            iridium.send(message) # Send through Iridium
        else:
            aprs.send(message) # Send through APRS
        sleep(get_config()['radio_output']['sleep_interval']) # Wait until APRS and Iridium buffers are cleared
    # At this point the lock has been released
