"""
Function kepel(r, v), where r is the input position vector, v is the
input velocity vector, and mu represents the EGM-96 value of the Earth's
gravitational constant, GM = 3.986004415E+14 m^3/sec^2. r and v units are in
meters. All angles in radians. r and v MUST BE numpy arrays.
Returns an array, KOE.
Retrieved from:
https://github.com/RazerM/orbital/blob/0.7.0/orbital/utilities.py#L252
Refer to kep2cart.py for orbitalpy and astropy installation instructions.
Created by Jason Chen 10/8/18
"""
import numpy as np
import math
from numpy import dot, arccos as acos
from numpy.linalg import norm
from scipy.constants import pi
from math import radians
from orbital import KeplerianElements, elements, utilities, earth
from orbital.utilities import (Position, Velocity, angular_momentum,
                               node_vector, eccentricity_vector, specific_orbital_energy)


def kepel(r, v):
    mu = 3.986004415E+14
    h = angular_momentum(r, v)
    n = node_vector(h)
    ev = eccentricity_vector(r, v, mu)
    E = specific_orbital_energy(r, v, mu)
    a = -mu / (2 * E)
    e = norm(ev)
    SMALL_NUMBER = 1E-15
    # Inclination is the angle between the angular
    # momentum vector and its z component.
    i = acos(h.z / norm(h))
    if abs(i - 0) < SMALL_NUMBER:
        # For non-inclined orbits, raan is undefined;
        # set to zero by convention
        raan = 0
        if abs(e - 0) < SMALL_NUMBER:
            # For circular orbits, place periapsis
            # at ascending node by convention
            arg_pe = 0
        else:
            # Argument of periapsis is the angle between
            # eccentricity vector and its x component.
            arg_pe = acos(ev.x / norm(ev))
    else:
        # Right ascension of ascending node is the angle
        # between the node vector and its x component.
        raan = acos(n.x / norm(n))
        if n.y < 0:
            raan = 2 * pi - raan

        # Argument of periapsis is angle between
        # node and eccentricity vectors.
        arg_pe = acos(dot(n, ev) / (norm(n) * norm(ev)))

    if abs(e - 0) < SMALL_NUMBER:
        if abs(i - 0) < SMALL_NUMBER:
            # True anomaly is angle between position
            # vector and its x component.
            f = acos(r.x / norm(r))
            if v.x > 0:
                f = 2 * pi - f
        else:
            # True anomaly is angle between node
            # vector and position vector.
            f = acos(dot(n, r) / (norm(n) * norm(r)))
            if dot(n, v) > 0:
                f = 2 * pi - f
    else:
        if ev.z < 0:
            arg_pe = 2 * pi - arg_pe
        # True anomaly is angle between eccentricity
        # vector and position vector.
        f = acos(dot(ev, r) / (norm(ev) * norm(r)))
        if dot(r, v) < 0:
            f = 2 * pi - f
    KOE = np.array([a, e, i, raan, arg_pe, f])
    return KOE

# Sample Run:
# r = np.array([-2437060.023, -2437126.902, 6890579.186])
# v = np.array([5088.649, -5088.576, -0.024])
# print(kepel(r, v))
# Returns: [7712185.793304873, 0.0009998565957693001, 1.1070000000336715,
#           2.356199994947052, 1.5708534575885496, 6.283131851920631]
