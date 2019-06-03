from pathlib import Path

from pyorbital.orbital import Orbital

def load():
    orb = Orbital("TJREVERB", tle_file=(
        Path(__file__).parent.resolve() / "tjreverb_tle.txt"))

def get_lla(t): #t is a datetime object
    load()
    return({'lat': orb.get_lonlatalt(t)[0], 'lon': orb.get_lonlatalt(t)[1], 'alt': orb.get_lonlatalt(t)[2]})

def get_xyz(t): #t is a datetime object
    load()
    return({'xyz_pos': orb.get_position(t)[0], 'xyz_vel': orb.get_position(t)[1]})

def can_TJ_be_seen(t): #t is a datetime object
    load()
    a=orb.get_next_passes(t, 1, -77.1687977, 38.8183519, .08, tol=0.001, horizon=0)
    return(a[0][0]<=t and t<=a[0][1])

def get_next_passes(t): #t is a datetime object
        return(orb.get_next_passes(t, 1, -77.1687977, 38.8183519, .08, tol=0.001, horizon=0))
