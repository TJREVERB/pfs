class Radio:
    """ Abstract radio class which both APRS and Iridium extend """

    def start(self):
        raise NotImplementedError

    def enter_low_power_mode(self):
        raise NotImplementedError

    def enter_normal_mode(self):
        raise NotImplementedError

    def set_modules(self, **kwargs):
        raise NotImplementedError

    def has_modules(self):
        raise NotImplementedError

    def send(self, message):
        raise NotImplementedError

    def listen(self):
        raise NotImplementedError
