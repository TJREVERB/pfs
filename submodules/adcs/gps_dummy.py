from datetime import datetime
import numpy as np


def get_data():
    return [{'lat': 5.3357, 'lon': -1.3483e+02, 'alt': 3.9685e+05, 'time': datetime.utcnow(), 'x_pos': 3000000.,
             'y_pos': 5000000., 'z_pos': 1000000., 'x_vel': 3000., 'y_vel': 3000., 'z_vel': 5000.}]


def data_is_valid(data):
    # if np.linalg.norm(data[0]['lat']) <= 1:
    #    return True
    return True
