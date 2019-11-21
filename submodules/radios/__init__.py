from submodules.submodule import Submodule


class Radio(Submodule):
    """ Abstract radio class which both APRS and Iridium extend """

    def __init__(self, name, config):
        """
        Instantiates a new Radio instance
        :param name: name of the radio("aprs" or "iridium")
        :param config: dictionary of configuration data
        """
        Submodule.__init__(self, name, config)

    def send(self, message) -> None:
        """
        Sends a message through the Radio
        :param message: message to sent
        :return: None
        """
        raise NotImplementedError

    def listen(self) -> None:
        """
        Listens for incoming message on Radio
        :return: None
        """
        raise NotImplementedError
