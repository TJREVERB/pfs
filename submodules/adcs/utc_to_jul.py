import math
from math import floor
from datetime import datetime as dt
"""
https://github.com/dannyzed/julian/blob/master/julian/julian.py
"""


def utc_to_jul(epoch):
    a = math.floor((14-(epoch.month))/12)
    y = epoch.year + 4800 - a
    m = epoch.month + 12*a - 3
    jdn = epoch.day + math.floor((153*m + 2)/5) + 365*y + math.floor(y/4) - \
        math.floor(y/100) + math.floor(y/400) - 32045
    jd = jdn + (epoch.hour - 12) / 24 + epoch.minute / 1440 + \
        epoch.second / 86400 - 2415020.5  # Subtracting dates since Jan 1, 1900
    # + dt.microsecond / 86400000000
    return jd
# print(utc_to_jul(dt.utcnow()))
