from threading import Timer


def delay(target, delay_time):
    """
    Run a given function after `delay_time` number of seconds.
    :param target: The child function to run.
    :param delay_time: Amount of time to delay run by (sec.).
    :return: A reference to the `threading.Timer` object that was created.
    """
    function_timer = Timer(delay_time, target)  # Create the Timer, which automatically uses a thread
    function_timer.start()
    return function_timer
