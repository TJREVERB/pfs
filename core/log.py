from datetime import datetime

class Log():
    def __init__(self, sys_name='CORE', lvl='INFO', ts=datetime.utcnow(), msg=None):
        self.system = sys_name
        self.level = lvl
        self.timestamp = ts
        self.message = msg
        self.header = 'LOG&'
    def to_string(self):
        return "{0}:{1}:{2}:{3}:{4}|".format(self.header, self.system, self.level,
            self.timestamp.strftime("%Y/%m/%d@%H%M%S"), self.message)
