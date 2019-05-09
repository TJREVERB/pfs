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
