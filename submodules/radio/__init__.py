class Radio:
    """ Abstract radio class which both APRS and Iridium extend """

    def send(self, message):
        raise NotImplementedError

    def listen(self):
        raise NotImplementedError
