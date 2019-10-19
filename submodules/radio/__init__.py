class Radio:
    """ Abstract radio class which both APRS and Iridium extend """

    def set_modules(self, **kwargs):
        raise NotImplementedError

    def send(self, message):
        raise NotImplementedError

    def listen(self):
        raise NotImplementedError
