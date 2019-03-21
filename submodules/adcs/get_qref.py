# BEING WORKED ON BY AYUSH
import numpy as np
from getDCM import getDCM
from numpy import linalg as LA
import math


def get_qref_nadir(poskep):
    for i in range(2, 6):
        poskep[0, i] = poskep[0, i]*math.pi/180
    q1 = np.matrix([0, 0, math.sin(poskep[0, 3]/2), math.cos(poskep[0, 3]/2)])
    q2 = np.matrix([math.sin(poskep[0, 2]/2), 0, 0, math.cos(poskep[0, 2]/2)])
    q3 = np.matrix([0, 0, math.sin((poskep[0, 4]+poskep[0, 5]+(math.pi/2))/2),
                    math.cos((poskep[0, 4]+poskep[0, 5]+(math.pi/2))/2)])
    q4 = np.matrix([math.sin((math.pi/2)/2), 0, 0, math.cos((-math.pi/2)/2)])
    qref = qmult(q1, q2)
    qref = qmult(qref, q3)
    qref = qmult(qref, q4)
    qref = np.divide(qref, LA.norm(qref))
    return qref


def get_qref_sun(poskep):
    for i in range(2, 6):
        poskep[0, i] = poskep[0, i]*math.pi/180
    sun = sunsensors()  # return column vector
    z = getDCM(bV, sV, bI, sI) * np.matrix([0, 0, 1]).getH()
    vecu = np.cross(sun, z)
    uma = LA.norm(vecu)
    vecu = vecu/uma
    thetadegrees = math.asin(uma) * 180/math.pi
    alpha = 90-thetadegrees
    qref = np.matrix([[vecu*math.sin((alpha/2)*math.pi/180)],
                      [math.cos((alpha/2)*math.pi/180)]])
    return qref


def qmult(q1, q2):
    q1 = np.squeeze(np.asarray(q1))
    q2 = np.squeeze(np.asarray(q2))
    q1 = q1.reshape(-1, 1)
    q2 = q2.reshape(-1, 1)
    comp1 = np.matrix([[q2.item(3), q2.item(2), -q2.item(1), q2.item(0)], [-q2.item(2), q2.item(3), q2.item(0), q2.item(1)],
                       [q2.item(1), -q2.item(0), q2.item(3), q2.item(2)], [-q2.item(0), -q2.item(1), -q2.item(2), q2.item(3)]])
    comp2 = np.matrix([[q1.item(0)], [q1.item(1)], [q1.item(2)], [q1.item(3)]])
    return (comp1*comp2).getH()
