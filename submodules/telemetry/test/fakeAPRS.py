from time import time, sleep

from submodules.radios import Radio


class fakeAPRS(Radio):
    def __init__(self, config):
        Radio.__init__(self, "aprs", config)
        self.last_telem_time = time()
        self.last_message_time = time()

    def set_modules(self, modules):
        self.modules = modules

    def has_modules(self):
        return len(self.modules) != 0

    def start(self):
        """
        Since this doesn't use serial, just a dummy function
        """
        pass

    def send(self, message):
        """
        Print message to stdout
        :param message: Message
        :return: None
        """
        print("APRS: Received send command")
        print(message)