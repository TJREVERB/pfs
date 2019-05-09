import numpy as np
from numpy import linalg

def get_mc(tc,b,mmax,mtrans):
    tc = tc.getH()
    b = b.getH()                                                            
    magdip = np.asmatrix((np.cross(b,tc)/(np.linalg.norm(b)**2)))
    magdip = mtrans*magdip.getH()
    magdip = magdip.getH()     
    big = max(abs(min(np.asarray(magdip).tolist()[0])), max(np.asarray(magdip).tolist()[0]))
    magdip = magdip/big*mmax
    magdip = magdip*mtrans
    return magdip
