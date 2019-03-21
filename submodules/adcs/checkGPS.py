# Written by Bharath Dileepkumar
# March 21, 2018

import tle_dummy


def checkGPS(lat, long, alt, time):
    tle = tle_dummy.get_lla(time)
    if(abs(lat - tle["lat"]) > 2 or abs(long - tle["lon"]) > 2 or abs(alt - tle["alt"]) > 2):
        return False
    else:
        return True
