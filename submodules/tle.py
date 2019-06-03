from pathlib import Path

from pyorbital.orbital import Orbital

def load():
    orb = Orbital("TJREVERB", tle_file=(
        Path(__file__).parent.resolve() / "tjreverb_tle.txt"))

def get_lla(t):
    load()
    return({'lat': orb.get_lonlatalt(t)[0], 'lon': orb.get_lonlatalt(t)[1], 'alt': orb.get_lonlatalt(t)[2]})


def get_xyz(t):
    load()
    return({'xyz_pos': orb.get_position(t)[0], 'xyz_vel': orb.get_position(t)[1]})
