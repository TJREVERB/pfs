from pathlib import Path

from pyorbital.orbital import Orbital

def can_TJ_be_seen(t):
  orb = Orbital("TJREVERB", tle_file=(
        Path(__file__).parent.resolve() / "tjreverb_tle.txt"))
  a=orb.get_next_passes(t, 1, -77.1687977, 38.8183519, .08, tol=0.001, horizon=0)
  return(a[0][0]<=t and t<=a[0][1])
