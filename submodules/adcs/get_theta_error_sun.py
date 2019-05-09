import numpy as np
from .get_dcm import get_dcm
from .q_mult import q_mult
from numpy import linalg as LA
import math

def get_theta_error_sun(poskep):
    for i in range(2, 6):
        poskep[0, i] = poskep[0, i]*math.pi/180
    sun = sun_sensor()  # return column vector
    z = getDCM(bV, sV, bI, sI) * np.matrix([0, 0, 1]).getH()
    theta = math.acos(np.dot(sun, z))
    vecu = np.cross(sun, z)
    uma = LA.norm(vecu)
    vecu = vecu/uma
    thetadegrees = math.asin(uma) * 180/math.pi
    alpha = 90-thetadegrees
    qref = np.matrix([[vecu*math.sin((alpha/2)*math.pi/180)],
                      [math.cos((alpha/2)*math.pi/180)]])
    return qref
