from datetime import datetime


class Log():
    """
    A class representing log messages.
    """

    def __init__(self, sys_name: str = 'CORE', lvl: str = 'INFO', ts: datetime = datetime.utcnow(), msg: str = None):
        """
        Constructor.
        :param sys_name: Subsystem name
        :param lvl: Level of message (info, warning, error)
        :param ts: Timestamp in datetime format.
        :param msg: String message
        """
        self.system = sys_name
        self.level = lvl
        self.timestamp = ts
        self.message = msg
        self.header = 'LOG&'


    def to_string(self):
        """
        :return: String representation of log message.
        """
        return "{0}:{1}:{2}:{3}:{4}".format(self.header, self.system, self.level,
                                            self.timestamp.strftime("%Y/%m/%d@%H%M%S"), self.message)
