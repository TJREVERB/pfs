import logging
import time


def threadhandler(func, parent_logger=logging, interval=3, suppress_out=False, *func_params):
    """Handles the starting of threads, and restarts them when they throw an exception.

    :param func: the child function to run
    :param parent_logger: a logging object (ex. GPS); default 'root'
    :param interval: amount of time between checking the status of the child function; default 3s
    :param suppress_out: suppresses the logging of messages; default False
    :param func_params: any parameters that need to be passed to the child function
    """

    def start():
        while True:
            if not suppress_out: parent_logger.info("'%s' thread started" % func.__name__)
            try:
                if len(func_params) > 0:
                    func(func_params)
                else:
                    func()
            except BaseException as e:
                if not suppress_out: parent_logger.exception(str(e) + ", restarting '%s'" % func.__name__)
            else:
                if not suppress_out: parent_logger.info("Bad thread, restarting '%s'" % func.__name__)
            time.sleep(interval)

    return start
