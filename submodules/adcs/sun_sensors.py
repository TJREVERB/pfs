#   Three inputs
#   theta = input vector with angle of incidence on the ZY plane for each sun sensor
#   phi = input vector with angle of incidence on the XY plane for each sun sensor
#   m = input vector with magnitude (voltage on 4 quadrants) for each sun vector
#   input vector order [+X panel, -X panel, +Y panel, -Y panel, +Z panel]
#   Outputs a sun vector in the vehicle frame
#   Bryan Zhang 11/30/2018

import numpy as np
import math
from math import sin, cos


def sun_sensors(theta, phi, m):
    #   Finds largest input voltage from the 5 sun sensors
    """
    NO BUENO, NEED TO DO WEIGHT AVERAGING OF THE SUN SENSOR MEASUREMENTS
    :param theta:
    :param phi:
    :param m:
    :return:
    """
    #   Creates a unit sun vector in vehicle frame and rotates it based on which sunsensor was used
    I = np.argmax(m)
    th = theta[I]
    ph = phi[I]
    vec = np.array(
        [[sin(th)*cos(ph)], [sin(th)*sin(ph)], [cos(th)]], np.float32)
    if I == 0:  # +X
        temp = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]])
        vec = np.matmul(temp, vec)
    elif I == 1:  # -X
        temp = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]])
        vec = np.matmul(temp, vec)
    elif I == 2:  # +y
        temp = np.array([[-1, 0, 0], [0, 1, 0], [1, 0, 0]])
        vec = np.matmul(temp, vec)
    elif I == 3:  # -Y
        temp = np.array([[0, 0, 1], [0, 1, 0], [-1, 0, 0]])
        vec = np.matmul(temp, vec)
    elif I == 4:  # +Z
        return vec
    return vec
