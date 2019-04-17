# Converted by Ayush Rautwar
# October 30th, 2018


from numpy import linalg
import numpy as np

# print get_dcm([1,2,3,4], [1,2,3,4], [1,2,3,4], [1,2,3,4])

# bV and sV converted on board
# Know instantaneous time, at any measurement (possibly from the GPS)
# Convert GPS time to UTC Time
# Interface between data and ADCS
# ecef2eci (should be from a toolbox)


def q_to_dcm(q):
    R = np.zeros((3, 3))

    R[0, 0] = q[0] ^ 2-q[1] ^ 2-q[2] ^ 2+q[3] ^ 2
    R[0, 1] = 2*(q[0]*q[1]+q[2]*q[3])
    R[0, 2] = 2*(q[0]*q[2]-q[1]*q[3])

    R[1, 0] = 2*(q[0]*q[1]-q[2]*q[3])
    R[1, 1] = -q[0] ^ 2+q[1] ^ 2-q[2] ^ 2+q[3] ^ 2
    R[1, 2] = 2*(q[1]*q[2]+q[0]*q[3])

    R[2, 0] = 2*(q[0]*q[2]+q[1]*q[3])
    R[2, 1] = 2*(q[1]*q[2]-q[0]*q[3])
    R[2, 2] = -q[0] ^ 2-q[1] ^ 2+q[2] ^ 2+q[3] ^ 2

    return R
# def get_dcm(bV, sV, bI, sI):
#  for i in bV:
#    i = i*1.00
#  for i in sV:
#    i = i*1.00
  # for i in bI:
#    i = i*1.00
  # for i in sI:
#    i = i*1.00


def get_dcm(bV, sV, bI, sI):
    #bV = np.matrix([bV])
    #sV = np.matrix([sV])
    #bI = np.matrix([bI])
    #sI = np.matrix([sI])

    bV = np.reshape(bV, (1, -1))/linalg.norm(bV)
    sV = np.reshape(sV, (1, -1))/linalg.norm(sV)  #
    bI = np.reshape(bI, (1, -1))/linalg.norm(bI)  #
    sI = np.reshape(sI, (1, -1))/linalg.norm(sI)  #

    vu2 = np.asmatrix(np.cross(bV, sV))
    vu2 = np.asmatrix(vu2/linalg.norm(vu2))
    vmV = np.hstack(
        (np.asmatrix(bV).getH(), vu2.getH(), np.asmatrix(np.cross(bV, vu2)).getH()))
    iu2 = np.asmatrix(np.cross(bI, sI))
    iu2 = np.asmatrix(iu2/linalg.norm(iu2))
    imV = np.hstack(
        (bI.getH(), iu2.getH(), np.asmatrix(np.cross(bI, iu2)).getH()))
    ivDCM = np.asmatrix(vmV)*np.asmatrix(imV).getH()
    return ivDCM

# q = normalize([0.1 0.2 -0.3 1].getH())
# R = q_to_dcm(q)
# bi = normalize([1 2 3].getH())
# si = normalize([-1 3 -2].getH())
# bv = R*bi
# sv = R*si
# RR = get_dcm(bv, sv, bi, si)
# dR = R - RR

# get_dcm([1,2,3],[1,2,3],[1,2,3],[1,2,3])
# get_dcm([1,2],[1,2],[1,2],[1,2])
# get_dcm([0.1,0.2,0.3],[0.1,0.2,0.3],[0.1,0.2,0.3],[0.1,0.2,0.3])
# get_dcm([0.1,0.2,0.3,0.4],[0.1,0.2,0.3,0.4],[0.1,0.2,0.3,0.4],[0.1,0.2,0.3,0.4])
# get_dcm([1.0,2.0,3.0],[1.0,2.0,3.0],[1.0,2.0,3.0],[1.0,2.0,3.0])
# get_dcm([1.0,2.0,3.0,4.0],[1.0,2.0,3.0,4.0],[1.0,2.0,3.0,4.0],[1.0,2.0,3.0,4.0])
# get_dcm([0.001,0.002,0.003],[0.001,0.002,0.003],[0.001,0.002,0.003],[0.001,0.002,0.003])
# get_dcm([10.0,20.0,30.0],[10.0,20.0,30.0],[10.0,20.0,30.0],[10.0,20.0,30.0])
# get_dcm([1.0],[1.0],[1.0],[1.0])
# get_dcm([1.0,2.0,3.0,4.0,5.0],[1.0,2.0,3.0,4.0,5.0],[1.0,2.0,3.0,4.0,5.0],[1.0,2.0,3.0,4.0,5.0])


# SHD: I recommend having a test program to test the logic of this function.
# For example, see below. I commented out so it doesn’t run, but uncomment and
# paste the lines to the Command window to check. Be sure to comment the
# lines again and save this function before actually executing the line in
# the Command window.
# q = [.1 .2 -.3 1]‘;q=q/norm(q); # Made-up quaternion from inertial to vehicle frame
# R = q_to_dcm(q);
# bi = [1 2 3]‘;bi=bi/norm(bi); # Made-up b vector in inertial frame
# si = [-1 3 -2]’;si=si/norm(si); # Made-up s vector in inertial frame
# bv = R*bi;
# sv = R*si;
# RR = get_dcm(bv,sv,bi,si); # Run the made-up vectors through the routine
# dR = R-RR # This should be close to zero
