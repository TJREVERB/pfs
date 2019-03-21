from orbital.utilities import Position, Velocity
from orbital import earth, KeplerianElements, utilities
import numpy as np
"""
Function kep_to_cart(KOE), returns Cartesian position/velocity vectors
[[R],[V]] from Keplerian orbital elements (KOE), using the EGM-96 value
of Earth's gravitational constant, GM = 3.986004415E+14 m^3/sec^2. All
angles are in radians. Position vector given in meters, velocity vector
given in meters/second.
***IMPORTANT***
KOE is an array of 6 values. KOE is defined as in kepel.py, as follows:
    KOE[0] = a = semi-major axis
    KOE[1] = e = eccentricity
    KOE[2] = i = inclination
    KOE[3] = raan = right ascension of the ascending node
    KOE[4] = arg_pe = argument of periapse
    KOE[5] = M0 = true anomaly
    body = reference body (dictates GM value)
    ref_epoch = optional reference time frame
***************
Created by Jason Chen 10/6/18
"""
"""
TO USE ASTROPY/ORBITALPY:
pip install -U pytest
pip install clang
pip install --upgrade setuptools
pip install astropy --no-deps
IF YOU ENCOUNTER THIS ERROR: Microsoft Visual C++ 14.0 is required.
GO TO: https://visualstudio.microsoft.com/visual-cpp-build-tools/
INSTALL: Build Tools for Visual Studio 2017
ONCE THE EXE IS RUNNING, INSTALL THE CORE C++ PACKAGE (around 5.3 GB).
TRY AGAIN: pip install astropy
pip install orbitalpy
"""


def kep_to_cart(KOE):
    orbitx = KeplerianElements(a=KOE[0], e=KOE[1], i=KOE[2], raan=KOE[3],
                               arg_pe=KOE[4], M0=KOE[5], body=earth)
    cart = np.array([list(orbitx.r), list(orbitx.v)])
    return cart


"""
Test input:
    KOE = [7712185.793304873, 0.0009998565957693001, 1.1070000000336715,
            2.356199994947052, 1.5708534575885496, 6.283131851920631]
    print(kep_to_cart(KOE))
Test output:
    [[-2.43706002e+06 -2.43712690e+06  6.89057919e+06]
     [ 5.08864926e+03 -5.08857647e+03 -2.36413505e-02]]
"""
