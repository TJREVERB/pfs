import logging

logger = logging.getLogger("ADCS")


def updateVals(msg):
    """
    Saves and updates GPS values.
    :param msg: What to set as `velocity_data`.
    """
    global velocity_data
    velocity_data = msg


def on_startup():
    # runs on application start - start any threads you need here
    pass


# TODO: Need to know what needs to be done in normal, low power, and emergency modes.
def enter_normal_mode():
    """
    Enter normal power mode. Update the GPS module internal coordinates every **10** minutes.
    """
    pass


def enter_low_power_mode():
    """
    Enter low power mode. Update the GPS module internal coordinates every **60** minutes.
    """
    pass


def enter_emergency_mode():
    """
    Enter emergency power mode.
    """
    pass


# TODO: Update these methods. Currently only holds placeholder methods.
def get_pry():
    return -1, -1, -1


def get_mag():
    return -1, -1, -1


def get_abs():
    return -1, -1, -1


def can_TJ_be_seen():
    return True  # TODO: Fix this method.
