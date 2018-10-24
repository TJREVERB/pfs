import time
import threading

def threadhandler(func, parentLogger, *funcParams):
    def start():
        while True:
            parentLogger.info("'%s' thread started" % func.__name__)
            try:
                if len(funcParams) > 0:
                    func(funcParams)
                else:
                    func()
            except BaseException as e:
                parentLogger.exception(str(e) + ", restarting '%s'" % func.__name__)
            else:
                parentLogger.info("Bad thread, restarting '%s'" % func.__name__)
            time.sleep(3)

    return start