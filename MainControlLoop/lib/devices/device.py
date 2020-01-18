import logging


class Device:
    def __init__(self, name, config):
        self.name = name
        self.config = config
        self.logger = logging.getLogger(self.name)

    def is_functional(self):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def disable(self):
        raise NotImplementedError
