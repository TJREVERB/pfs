# Written by Bharath Dileepkumar
# March 21, 2018

from . import tle_dummy


def check_gps(lat, long, alt, time):
    tle = tle_dummy.get_lla(time)
    if(abs(lat - tle["lat"]) > 5 or abs(long - tle["lon"]) > 5 or abs(alt - tle["alt"]) > 5):
        return False
    else:
        return True
