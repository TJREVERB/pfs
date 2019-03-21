# INPUTS: Cartesian state vectors:
# Position: r(t)
# Velocity: dr/dt
# Gravitational constant
# Mass of earth
#
# OUTPUTS: Keplarian elements [a escalar w l i m]
# Semi-major axis, a
# Eccentricity, e
# Argument of periapsis, w
# Longitude of ascending node, l
# Inclination, i
# Mean anomaly, m
# NOTE: Epoch is not detemined in this function as of yet.

import numpy as np
import math


def cart2kep(r, vel):
    r = [float(i) for i in r]
    vel = [float(i) for i in vel]
    G = 6.67408 * (10**(-11))  # Gravitational constant(N kg^-2 m^2)
    M = 5.9722 * (10**(24))  # Mass of Earth (kg)
    GM = G*M  # Constant parameter
    # Constant (z-axis) used with angular momentum to calculate ascending node
    k = np.array([0, 0, 1])
    # Orbital momentum (without mass dimension): r cross vel
    h = np.cross(r, vel)
    n = np.cross(k, h)  # Vector from Earth center to ascending node

    # Eccentricity vector and eccentricity: (e, escalar)
    e = np.cross(vel, h)/GM - r/np.linalg.norm(r)
    escalar = np.linalg.norm(e)

    # True anomaly: (v)
    if np.dot(r, vel) >= 0:
        v = math.acos(np.dot(e, r)/(np.linalg.norm(e) * np.linalg.norm(r)))
    else:
        v = 2*np.pi - math.acos(np.dot(e, r) /
                                (np.linalg.norm(e) * np.linalg.norm(r)))

    # Inclination: (i)
    i = math.acos(h[2]/np.linalg.norm(h))

    # Eccentric anomaly: (E)
    # Reference: https://en.wikipedia.org/wiki/Eccentric_anomaly
    E = 2*math.atan(math.tan(v/2)/math.sqrt((1+escalar)/(1-escalar)))

    # Longitude of the ascending node: (l)
    if n[1] >= 0:
        l = math.acos(n[0]/np.linalg.norm(n))
    else:
        l = 2*math.pi - math.acos(n[0]/np.linalg.norm(n))

    # Argument of periapsis: (w)
    if e[2] >= 0:
        w = math.acos(np.dot(n, e)/(np.linalg.norm(n) * np.linalg.norm(e)))
    else:
        w = 2*math.pi - math.acos(np.dot(n, e) /
                                  (np.linalg.norm(n) * np.linalg.norm(e)))

    # Mean anomaly: (m)
    m = E - escalar*math.sin(E)

    # Semi-major axis: (a)
    a = 1/(2/np.linalg.norm(r) - (np.linalg.norm(vel)**2)/GM)
    return np.array([a, escalar, w, l, i, m])

# r = [3000000., 5000000., 1000000.]
# vel = [3000., 3000., 5000.]
# print(cart2kep(r, vel))
