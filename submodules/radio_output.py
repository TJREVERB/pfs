from submodules import aprs
from submodules import iridium

default_radio: str = "aprs"
aprs = "aprs"
iridium = "iridium"


def send(message: str, radio=None):
    """
    Send a message back to the groundstation.
    :param message: Message to send to the radio.
    :param radio: Radio to which to send the message. If `None`, send to the default radio.
    """
    if radio is None:
        radio = default_radio
    if radio == "aprs":
        aprs.send(message)
        #print("RADIO_OUTPUT:" + message)
    if radio == "iridium":
        iridium.enqueue(message)


def send_immediate_raw(packet):
    return None
