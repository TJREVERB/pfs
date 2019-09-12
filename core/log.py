from datetime import datetime

class Log():
    def __init__(self, sys_name='CORE', ts=datetime.now(), msg=None):
        self.system = sys_name
        self.timestamp = ts
        self.message = msg
        self.header = 'LOG&'
    def to_string(self):
        return "{0}:{1}:{2}:{3}".format(self.header, self.system, 
            self.timestamp.strftime("%Y/%m/%d@%H.%M.%S"), self.message)
