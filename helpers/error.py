from datetime import datetime


class Error():
    """
    A class representing error messages.
    """

    def __init__(self, sys_name='CORE', ts: datetime = datetime.utcnow(), msg: str = None):
        """
        Constructor.
        :param sys_name: The name of the subsystem.
        :param ts: A timestamp in datetime format.
        :param msg: A string representing the message.
        """
        self.system = sys_name
        self.timestamp = ts
        self.message = msg
        self.header = 'ERR!'

    def __str__(self) -> str:
        """
        :return: A string representation of this error.
        """
        return "{0}:{1}:{2}:{3}".format(self.header, self.system,
                                        self.timestamp.strftime("%Y/%m/%d@%H.%M.%S"), self.message)