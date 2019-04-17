# BEING WORKED ON BY AYUSH
import numpy as np
from .get_dcm import get_dcm
from .q_mult import q_mult
from numpy import linalg as LA
import math


def get_q_ref_nadir(poskep):
    for i in range(2, 6):
        poskep[i] = poskep[i]*math.pi/180
    q1 = np.matrix([0, 0, math.sin(poskep[3]/2), math.cos(poskep[3]/2)])
    q2 = np.matrix([math.sin(poskep[2]/2), 0, 0, math.cos(poskep[2]/2)])
    q3 = np.matrix([0, 0, math.sin((poskep[4]+poskep[5]+(math.pi/2))/2),
                    math.cos((poskep[4]+poskep[5]+(math.pi/2))/2)])
    q4 = np.matrix([math.sin((math.pi/2)/2), 0, 0, math.cos((-math.pi/2)/2)])
    qref = q_mult(q1, q2)
    qref = q_mult(qref, q3)
    qref = q_mult(qref, q4)
    qref = np.divide(qref, LA.norm(qref))
    return qref


def get_q_ref_sun(poskep):
    for i in range(2, 6):
        poskep[0, i] = poskep[0, i]*math.pi/180
    sun = sun_sensor()  # return column vector
    z = getDCM(bV, sV, bI, sI) * np.matrix([0, 0, 1]).getH()
    vecu = np.cross(sun, z)
    uma = LA.norm(vecu)
    vecu = vecu/uma
    thetadegrees = math.asin(uma) * 180/math.pi
    alpha = 90-thetadegrees
    qref = np.matrix([[vecu*math.sin((alpha/2)*math.pi/180)],
                      [math.cos((alpha/2)*math.pi/180)]])
    return qref
