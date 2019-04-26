from threading import Timer

from core import config


def delay(target, delay_time):
    """
    Run a given function after `delay_time` number of seconds.
    :param target: The child function to run.
    :param delay_time: Amount of time to delay run by (sec.).
    :return: A reference to the `threading.Timer` object that was created.
    """
    function_timer = Timer(
        delay_time, target)  # Create the Timer, which automatically uses a thread
    function_timer.start()
    return function_timer


def is_simulate(submodule):
    """
    Retrieve simulation mode status for a given submodule.
    :param submodule: Name of the submodule to retrieve simulation mode for, as a String.
    :return: `True` if the submodule is in simulate mode, `False` if not.
    """
    try:  # Attempt to retrieve the key from the config file
        is_sim = config[submodule]['simulate']
        if not type(is_sim) is bool:  # The key is not a boolean
            return False
        else:
            return is_sim
    except KeyError:  # The key does not exist, assume not in simulation mode
        return False
