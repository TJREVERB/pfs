def get_theta_err(q):
    q = q.getH()
    thetaerr = 2*(q[0:3]/q[3])
    return thetaerr
