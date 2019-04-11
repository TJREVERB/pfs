from pathlib import Path

from .get_q_ref import *
from .get_dcm import get_dcm
from .get_theta_err import get_theta_err
from .get_q_err import get_q_err
from .kep_to_cart import kep_to_cart
from .dec_year import dec_year
from .sun_vec import sun_vec
from .sun_sensors import sun_sensors
from .utc_to_jul import utc_to_jul
from .wrldmagm import WrldMagM
from .cart_to_kep import cart_to_kep
from .get_mc import get_mc
from .dcm_to_q import dcm_to_q
from core import load_config

from . import gps_dummy
from . import tle_dummy
from . import tle_points

import numpy as np
from datetime import datetime, date
from pymap3d import ecef2eci

import logging

logger = logging.Logger("ADCS")


def gps_is_on():
    return True

def start():
    global epoch
    global revnum
    global lastmeananom
    global lasttime
    global lastmeanmot

    revnum =0
    lasttime=datetime(2018, 4, 4)
    lastmeananom=0
    lastmeanmot=15.5
    gain = 2*(10**(-5))


    config = load_config()  # Load the data from the YAML.
    # If GPS is on, get Cartesian (position, velocity) vectors and UTC time from the GPS.
    # Convert Cartesian coordinates and time to a Keplerian Elements array.
    # Generate a new TLE using the KOE.

    if gps_is_on():  # If we ask for GPS coordinates and the GPS responds:
        # Data is a list (cache) of dictionaries representing one timestep.
        data = gps_dummy.get_data()
        if gps_dummy.data_is_valid(data):  # If the data is valid:
            i = len(data)-1  # Get the last dictionary in the cache.
            # Position state vector.
            r = [data[i]['x_pos'], data[i]['y_pos'], data[i]['z_pos']]  # ECI frame
            # Velocity state vector.
            vel = [data[i]['x_vel'], data[i]['y_vel'], data[i]['z_vel']]
            epoch = data[i]['time']  # Datetime object representing the epoch.

            # Convert state vectors into an array representing the KOE.
            koe_array = cart_to_kep(r, vel)
            koe_list = koe_array.tolist()
            # koe_array = np.insert(koe_array, 0, epoch)  # Add the datetime object epoch to the beginning.
            koe_list.insert(0, epoch)
            # koe_array = np.append(koe_array, data['adcs']['tledata']['bstardrag'])  # Append the B-star drag coefficient
            koe_list.append(config['adcs']['sc']['bstardrag'])
            temp_tle, lastmeanmot, lastmeananom, lasttime = tle_points.propagate(koe_list, lastmeanmot, lastmeananom, lasttime, revnum)  # Generate the new TLE.

            # print(koe_list)
            # print(temp_tle)

            tjreverbtle = open(config['adcs']['tlefiles']['tjreverb'], "w")  # Open the main TJREVERB TLE for writing.
            tjreverbtle.write(temp_tle)  # Write the new TLE to TJREVERB TLE.
            tjreverbtle.close()  # Close the file.

            # Backup the TLE data.
            backuptle = open(config['adcs']['tlefiles']['backup'], "w")
            backuptle.write(temp_tle)
            backuptle.close()

            lla = tle_dummy.get_lla(epoch)  # Pull LLA data from TJREVERB TLE.
        else:  # If the GPS is on but the data is invalid:
            epoch = datetime.utcnow()  # Set current time to the system time.
            # Uses PyOrbital to propogate the TLE using epoch, which returns its LLA.
            lla = tle_dummy.get_lla(epoch)

    # If GPS is off, use the system time and TJREVERB TLE to propogate the current LLA.
    else:  # If we ask for GPS coordinates and the GPS not respond:
        epoch = datetime.utcnow()  # Set current time to the system time.
        # Uses PyOrbital to propogate the TLE using epoch, which returns its LLA.
        lla = tle_dummy.get_lla(epoch)

    # needed to incremement revnum
    print(tle_dummy.get_xyz(epoch)['xyz_pos'])
    print(tle_dummy.get_xyz(epoch)['xyz_vel'])
    print(tle_dummy.get_lla(epoch))
    pos = []
    vel = []
    for i in tle_dummy.get_xyz(epoch)['xyz_pos']:
        pos.append(i*1000)
    for j in tle_dummy.get_xyz(epoch)['xyz_vel']:
        vel.append(j*1000)
    poskep = cart_to_kep(pos, vel)
    print("KOE (from newly generated TLE): "+str(poskep))
    # if (poskep[4]>0 and oldargp<=0):
    #     revnum=revnum+1
    # oldargp = poskep[4]

    # write_config('config_adcs.yaml', utc_to_jul(epoch))  # config['adcs']['sc']['jd0'] = utc_to_jul(epoch)
    # Instantiates the WrldMagM object.
    gm = WrldMagM((Path(__file__).parent.resolve() /
                   config['adcs']['wrldmagm']))

    # Calculate the magnetic field vector in ECEF. Altitude is multiplied to convert meters to feet.
    magECEF = gm.wrldmagm(lla['lat'], lla['lon'], lla['alt'], date.today())

    magECEF = np.squeeze(np.asarray(magECEF))
    magECI = ecef2eci(magECEF, epoch)

    # Magnetic field in inertial frame, converts teslas to nanoteslas.
    bI = 1.0*(10e-09) * magECI
    bI = bI/np.linalg.norm(bI)
    bI = np.asmatrix(bI)
    bI = bI.getH()

    # Sun vector in intertial frame.
    sI = sun_vec(utc_to_jul(epoch)-utc_to_jul(datetime(1980, 1, 6, 0, 0, 0)))
    sI = sI/np.linalg.norm(sI)  # Normalize sI.

    print(bI)
    print(sI)

    # bV and sV data are taken from the onboard magnetometer and sunsensors.
    bV = [1,1,2]
    sV = [1,2,1]

    dcm = get_dcm(bV, sV, bI, sI)
    print("DCM: "+str(dcm))
    q = dcm_to_q(dcm)
    print("Quaternion: "+str(q))
    qref = get_q_ref_nadir(poskep)
    print("Reference Quaternion: "+str(qref))                      
    qerr = get_q_err(q, qref)      
    print("Quaternion Error: "+str(qerr))                    
    thetaerr = get_theta_err(qerr)
    print("Theta Error (radians): "+str(thetaerr.getH()))
    mmax = [.2,.2,.2]
    mtrans = np.matrix([[1,0,0],[0,1,0],[0,0,1]])
    ctcomm=-1*gain*thetaerr.getH()
    #print(ctcomm)
    magdip = get_mc(ctcomm.getH(),np.matrix([bV]).getH(),np.matrix([mmax]),mtrans)
    print("Magnetic Dipole (sent to imtq): "+str(magdip))
    ctprod = np.cross(magdip,bV)
    print("Control Torque Produced: "+str(ctprod))

    # isisimtq.py_k_imtq_start_actuation_dipole(imtq_axis_data(magdip[0], magdip[1], magdip[2]), 800)
