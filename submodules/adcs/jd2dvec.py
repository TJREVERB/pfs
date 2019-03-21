# Function jd2dvec(jd), returns array A
# Created by Jason Chen 10/5/18
# Converts input of a Julian date (a float), jd, to an array A,
# the equivalent Gregorian date [Year, Month, Day, Hour, Minute, Second]
# Requires from jdcal import gcal2jd, jd2gcal


def jd2dvec(jd):
    ps = jd - 2400000.5  # Done to increase time precision
    epochvec = list(jd2gcal(2400000.5, ps))  # Converts tuple to list
    hours = int(epochvec[3]*24)
    # Sets jdarray[4] to decimal of hours
    epochvec.append(epochvec[3]*24 - hours)
    epochvec[3] = hours
    minutes = int(epochvec[4]*60)
    epochvec.append(epochvec[4]*60 - minutes)
    epochvec[4] = minutes
    epochvec[5] = (epochvec[5]*60)
    return epochvec
