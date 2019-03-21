# Function q2dcm(q), returns array R
# Created by Anonto Zaman, Translated to Python by Jason Chen
# Converts from a quaternion [vector;scalar] to a direction cosine matrix


def q2dcm(q):
    R = np.zeros((3, 3))

    R[0, 0] = q[0]**2-q[1]**2-q[2]**2+q[3]**2
    R[0, 1] = 2*(q[0]*q[1]+q[2]*q[3])
    R[0, 2] = 2*(q[0]*q[2]-q[1]*q[3])

    R[1, 0] = 2*(q[0]*q[1]-q[2]*q[3])
    R[1, 1] = -q[0]**2+q[1]**2-q[2]**2+q[3]**2
    R[1, 2] = 2*(q[1]*q[2]+q[0]*q[3])

    R[2, 0] = 2*(q[0]*q[2]+q[1]*q[3])
    R[2, 1] = 2*(q[1]*q[2]-q[0]*q[3])
    R[2, 2] = -q[0]**2-q[1]**2+q[2]**2+q[3]**2

    return R
