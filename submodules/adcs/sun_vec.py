# SUN_VEC Computes unit vector from origin of ECI frame to sun
#
#  [sun_equ] = sun_vec(start_day)
#
#  Inputs:    start_day    int: days since 00:00:00 01/06/1980
#
#  Outputs:   sun_equ      [3,1] Earth-Sun vector in an ECI frame
#
#  Given start_day measured in days since 01/06/80, computes true
#  longitude of the Sun.  Earth-Sun vector is then computed in the
#  ecliptic plane, and is rotated into the ECI frame (equatorial
#  plane).  # ephemeris days assumed equal to # Julian days
#  The Earth-Sun vector rotates approximately 1.02 deg/day
#
#  Reference: J.R. Wertz, p 141
# Bryan Zhang 10/11/2018

import numpy as np
import math
from math import sin, pi, cos


def sun_vec(start_day):
    # Julian days since Jan 0,1900
    #  Reference for this calculation is JD 2,415,020 which
    #  corresponds to 12:00:00 Jan 0,1900 ET (or 12:00:00 Dec 31,1899)
    jd = 29224.5 + start_day
    #  Mean longitude of sun, measured in the ecliptic from mean
    #  equinox of date:
    L = (279.696678 + 0.9856473354*jd + 2.267e-13*(jd**2))
    #  Mean anomaly of sun in radians
    Ms_r = (pi/180)*(358.475845 + 0.985600267*jd -
                     (1.12e-13)*(jd**2) - (7e-20)*(jd**3))
    #  Correction between mean longitude and true longitude
    dL = 1.918*sin(Ms_r) + 0.02*sin(2*Ms_r)
    #  True longitude of sun, in radians
    L_sun = ((pi/180)*(L+dL)) % (2*pi)
    #  Compute sun unit vector in ECI frame, where the Earth's
    #  equatorial plane is inclined inc_E radians to the ecliptic
    #  R defines a rotation about the x-axis
    inc_E = (pi/180)*(-23.45)
    # R = [1,0,0; 0,cos(inc_E),sin(inc_E); 0,-sin(inc_E),cos(inc_E)];# [3,3] #CONVERT
    # sun_ecl = [cos(L_sun);sin(L_sun);zeros(1,size(start_day,2))];  # [3,n]

    R = np.array([[1, 0, 0], [0, cos(inc_E), sin(inc_E)], [
                 0, -sin(inc_E), cos(inc_E)]], np.float32)
    sun_ecl = np.array([[cos(L_sun)], [sin(L_sun)], [0]], np.float32)
    #  Since R is constant through time, can do a simple matrix multiply
    sun_equ = np.matmul(R, sun_ecl)   # [3,1]
    return sun_equ
