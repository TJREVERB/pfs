class Radio:
    """ Abstract radio class which both APRS and Iridium extend """

    def __init__(self, serial_port):
        return

    def send(self, message):
        raise NotImplementedError
