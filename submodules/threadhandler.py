import functools
import logging
import time
import threading


class ThreadHandler:
    def __init__(self, target, name=None,
                 parent_logger=logging, interval=3, suppress_out=False, auto_restart=True):

        self.target = target

        self.name = name

        self.parent_logger = parent_logger
        self.interval = interval
        self.suppress_out = suppress_out
        self.auto_restart = auto_restart
        self.is_active = True
        self.is_alive = False

    def start(self):
        threading.Thread(target=self.run, name=self.name, daemon=True).start()

    def run(self):
        def start():
            while True:
                if self.is_active:
                    if not self.suppress_out: self.parent_logger.info("'%s' thread started" % self.name)
                    try:
                        self.target()
                    except BaseException as e:
                        if not self.suppress_out: self.parent_logger.exception(str(e) + ", restarting '%s'" % self.name)
                        if not self.auto_restart:
                            self.is_active = False
                    else:
                        if not self.suppress_out: self.parent_logger.info("Bad thread, restarting '%s'" % self.name)
                        if not self.auto_restart:
                            self.is_active = False
                time.sleep(self.interval)

        return start()

    def resume(self):
        if not self.suppress_out: self.parent_logger.info("'%s' thread resumed" % self.name)
        if not self.auto_restart:
            self.is_active = True

    def pause(self):
        if not self.suppress_out: self.parent_logger.info("'%s' thread paused" % self.name)
        if not self.auto_restart:
            self.is_active = False