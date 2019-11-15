from submodules import Submodule


class Radio(Submodule):
    """ Abstract radio class which both APRS and Iridium extend """

    def __init__(self, name, config):
        Submodule.__init__(self, name, config)

    def send(self, message):
        raise NotImplementedError

    def listen(self):
        raise NotImplementedError
