import logging


class Device:
    def __init__(self, name):
        self.name: str = name
        self.logger: logging.Logger = logging.getLogger(self.name)

    def is_functional(self):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def disable(self):
        raise NotImplementedError
