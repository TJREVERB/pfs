from datetime import datetime
import numpy as np


def get_data():
    return [{'lat': -16.8, 'lon': 50.65, 'alt': 414000., 'time': datetime.utcnow(), 'x_pos': -153.,
             'y_pos': 820., 'z_pos': -658., 'x_vel': 1500., 'y_vel': 300., 'z_vel': 100.}]


def data_is_valid(data):
    # if np.linalg.norm(data[0]['lat']) <= 1:
    #    return True
    return True
