import numpy as np
def q_mult(q1,q2):
    q1 = np.squeeze(np.asarray(q1))
    q2 = np.squeeze(np.asarray(q2))
    q1 = q1.reshape(-1, 1)
    q2 = q2.reshape(-1, 1)
    comp1 = np.matrix([[q2.item(3), q2.item(2), -q2.item(1), q2.item(0)],[-q2.item(2), q2.item(3), q2.item(0), q2.item(1)],[q2.item(1), -q2.item(0), q2.item(3), q2.item(2)],[-q2.item(0), -q2.item(1), -q2.item(2), q2.item(3)]])
    comp2 = np.matrix([[q1.item(0)],[q1.item(1)],[q1.item(2)],[q1.item(3)]])
    return((comp1*comp2).getH())
