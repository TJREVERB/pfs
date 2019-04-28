import math
import numpy as np
def dcm_to_q(dcm):
    q4 = .5*math.sqrt(1+dcm.item(0)+dcm.item(4)+dcm.item(8))
    q1 = (1/(4*q4))*(dcm.item(5)-dcm.item(7))
    q2 = (1/(4*q4))*(dcm.item(6)-dcm.item(2))
    q3 = (1/(4*q4))*(dcm.item(1)-dcm.item(3))
    q = np.array([q1,q2,q3,q4])
    return (q)
