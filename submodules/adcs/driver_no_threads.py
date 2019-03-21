import unittest
import os
import math
import pymap3d
from orbital.utilities import Position, Velocity
from orbital import earth, KeplerianElements, utilities
import time
from jdcal import gcal2jd, jd2gcal
from datetime import datetime, date
import datetime
from numpy import linalg
import numpy as np
"""
Overall ADCS driver program. Calculates sensor outputs given sample
sun_vec data and GPS data.

Completed 15 November, 2018.
"""
"""
SAMPLE RUN:

INPUT:

epoch =
    '08-Nov-2018 12:00:00.000'
sv =
    0.736594581345171
    -0.321367778737346
    0.595106018724694
bv =
    0.593302194154829
    -0.297353472232347
    -0.748046401610510
lat_deg =
    5.335745187657780
lon_deg =
    -1.348386750055788e+02
alt_meter =
    3.968562753276266e+05

OUTPUT:

    -0.851199700910797  -0.378355652210824   0.363739013042995

    -0.406178514058743   0.913793748455871  -0.000000000000000

    -0.332382436188197  -0.147742971822997  -0.931500901980512
"""


#import yaml
# with open("config.yml.sample", 'r') as ymlfile:
#    config = yaml.load(ymlfile)
#from core import config

"""""""""""""""""""""""
MAIN METHODS
"""""""""""""""""""""""


def utc2jul(dt):
    a = math.floor((14-dt.month)/12)
    y = dt.year + 4800 - a
    m = dt.month + 12*a - 3
    jdn = dt.day + math.floor((153*m + 2)/5) + 365*y + math.floor(y/4) - \
        math.floor(y/100) + math.floor(y/400) - 32045
    jd = jdn + (dt.hour - 12) / 24 + dt.minute / 1440 + \
        dt.second / 86400 - 2415020.5
    return jd


def sun_vec(start_day):
    jd = start_day
    L = (279.696678 + 0.9856473354*jd + 2.267e-13*(jd**2))
    Ms_r = (math.pi/180)*(358.475845 + 0.985600267*jd - (1.12e-13)*(jd**2) -
                          (7e-20)*(jd**3))
    dL = 1.918*math.sin(Ms_r) + 0.02*math.sin(2*Ms_r)
    L_sun = ((math.pi/180)*(L+dL)) % (2*math.pi)
    inc_E = (math.pi/180)*(-23.45)
    # R = [1,0,0; 0,cos(inc_E),sin(inc_E); 0,-sin(inc_E),cos(inc_E)];# [3,3]
    # sun_ecl = [cos(L_sun);sin(L_sun);zeros(1,size(start_day,2))];  # [3,n]
    R = np.array([[1, 0, 0], [0, math.cos(inc_E), math.sin(inc_E)],
                  [0, -math.sin(inc_E), math.cos(inc_E)]], np.float32)
    sun_ecl = np.array([[math.cos(L_sun)], [math.sin(L_sun)], [0]], np.float32)
    sun_equ = np.matmul(R, sun_ecl)   # [3,1]
    return sun_equ


def kep2cart(KOE):
    orbitx = KeplerianElements(a=KOE[0], e=KOE[1], i=KOE[2], raan=KOE[3],
                               arg_pe=KOE[4], M0=KOE[5], body=earth)
    cart = np.array([list(orbitx.r), list(orbitx.v)])
    return cart


def jd2dvec(jd):
    ps = jd - 2400000.5  # Done to increase time precision
    epochvec = list(jd2gcal(2400000.5, ps))  # Converts tuple to list
    hours = int(epochvec[3]*24)
    # Sets jdarray[4] to decimal of hours
    epochvec.append(epochvec[3]*24 - hours)
    epochvec[3] = hours
    minutes = int(epochvec[4]*60)
    epochvec.append(epochvec[4]*60 - minutes)
    epochvec[4] = minutes
    epochvec[5] = (epochvec[5]*60)
    return epochvec


class wrldmagm:

    # latitude (decimal degrees), longitude (decimal degrees), altitude (feet), date
    def wrldmagm(self, dlat, dlon, h, time):
        #time = date('Y') + date('z')/365
        #time = time.year+((time - date(time.year,1,1)).days/365.0)
        alt = h/3280.8399

        otime = oalt = olat = olon = -1000.0

        dt = time - self.epoch
        glat = dlat
        glon = dlon
        rlat = math.radians(glat)
        rlon = math.radians(glon)
        srlon = math.sin(rlon)
        srlat = math.sin(rlat)
        crlon = math.cos(rlon)
        crlat = math.cos(rlat)
        srlat2 = srlat*srlat
        crlat2 = crlat*crlat
        self.sp[1] = srlon
        self.cp[1] = crlon

        # /* CONVERT FROM GEODETIC COORDS. TO SPHERICAL COORDS. */
        if (alt != oalt or glat != olat):
            q = math.sqrt(self.a2-self.c2*srlat2)
            q1 = alt*q
            q2 = ((q1+self.a2)/(q1+self.b2))*((q1+self.a2)/(q1+self.b2))
            ct = srlat/math.sqrt(q2*crlat2+srlat2)
            st = math.sqrt(1.0-(ct*ct))
            r2 = (alt*alt)+2.0*q1+(self.a4-self.c4*srlat2)/(q*q)
            r = math.sqrt(r2)
            d = math.sqrt(self.a2*crlat2+self.b2*srlat2)
            ca = (alt+d)/r
            sa = self.c2*crlat*srlat/(r*d)

        if (glon != olon):
            for m in range(2, self.maxord+1):
                self.sp[m] = self.sp[1]*self.cp[m-1]+self.cp[1]*self.sp[m-1]
                self.cp[m] = self.cp[1]*self.cp[m-1]-self.sp[1]*self.sp[m-1]

        aor = self.re/r
        ar = aor*aor
        br = bt = bp = bpp = 0.0
        for n in range(1, self.maxord+1):
            ar = ar*aor

            # for (m=0,D3=1,D4=(n+m+D3)/D3;D4>0;D4--,m+=D3):
            m = 0
            D3 = 1
            # D4=(n+m+D3)/D3
            D4 = (n+m+1)
            while D4 > 0:

                # /*
                # COMPUTE UNNORMALIZED ASSOCIATED LEGENDRE POLYNOMIALS
                # AND DERIVATIVES VIA RECURSION RELATIONS
                # */
                if (alt != oalt or glat != olat):
                    if (n == m):
                        self.p[m][n] = st * self.p[m-1][n-1]
                        self.dp[m][n] = st*self.dp[m-1][n-1] + \
                            ct*self.p[m-1][n-1]

                    elif (n == 1 and m == 0):
                        self.p[m][n] = ct*self.p[m][n-1]
                        self.dp[m][n] = ct*self.dp[m][n-1]-st*self.p[m][n-1]

                    elif (n > 1 and n != m):
                        if (m > n-2):
                            self.p[m][n-2] = 0
                        if (m > n-2):
                            self.dp[m][n-2] = 0.0
                        self.p[m][n] = ct*self.p[m][n-1] - \
                            self.k[m][n]*self.p[m][n-2]
                        self.dp[m][n] = ct*self.dp[m][n-1] - st * \
                            self.p[m][n-1]-self.k[m][n]*self.dp[m][n-2]

        # /*
                # TIME ADJUST THE GAUSS COEFFICIENTS
        # */
                if (time != otime):
                    self.tc[m][n] = self.c[m][n]+dt*self.cd[m][n]
                    if (m != 0):
                        self.tc[n][m-1] = self.c[n][m-1]+dt*self.cd[n][m-1]

        # /*
                # ACCUMULATE TERMS OF THE SPHERICAL HARMONIC EXPANSIONS
        # */
                par = ar*self.p[m][n]

                if (m == 0):
                    temp1 = self.tc[m][n]*self.cp[m]
                    temp2 = self.tc[m][n]*self.sp[m]
                else:
                    temp1 = self.tc[m][n]*self.cp[m]+self.tc[n][m-1]*self.sp[m]
                    temp2 = self.tc[m][n]*self.sp[m]-self.tc[n][m-1]*self.cp[m]

                bt = bt-ar*temp1*self.dp[m][n]
                bp = bp + (self.fm[m] * temp2 * par)
                br = br + (self.fn[n] * temp1 * par)
        # /*
                # SPECIAL CASE:  NORTH/SOUTH GEOGRAPHIC POLES
        # */
                if (st == 0.0 and m == 1):
                    if (n == 1):
                        self.pp[n] = self.pp[n-1]
                    else:
                        self.pp[n] = ct*self.pp[n-1]-self.k[m][n]*self.pp[n-2]
                    parp = ar*self.pp[n]
                    bpp = bpp + (self.fm[m]*temp2*parp)

                D4 = D4-1
                m = m+1

        if (st == 0.0):
            bp = bpp
        else:
            bp = bp/st
        # /*
            # ROTATE MAGNETIC VECTOR COMPONENTS FROM SPHERICAL TO
            # GEODETIC COORDINATES
        # */
        bx = -bt*ca-br*sa
        by = bp
        bz = bt*sa-br*ca
        # /*
        # COMPUTE DECLINATION (DEC), INCLINATION (DIP) AND
        # TOTAL INTENSITY (TI)
        # */
        bh = math.sqrt((bx*bx)+(by*by))
        ti = math.sqrt((bh*bh)+(bz*bz))
        dec = math.degrees(math.atan2(by, bx))
        dip = math.degrees(math.atan2(bz, bh))
        # /*
        # COMPUTE MAGNETIC GRID VARIATION IF THE CURRENT
        # GEODETIC POSITION IS IN THE ARCTIC OR ANTARCTIC
        # (I.E. GLAT > +55 DEGREES OR GLAT < -55 DEGREES)

        # OTHERWISE, SET MAGNETIC GRID VARIATION TO -999.0
        # */
        gv = -999.0
        if (math.fabs(glat) >= 55.):
            if (glat > 0.0 and glon >= 0.0):
                gv = dec-glon
            if (glat > 0.0 and glon < 0.0):
                gv = dec+math.fabs(glon)
            if (glat < 0.0 and glon >= 0.0):
                gv = dec+glon
            if (glat < 0.0 and glon < 0.0):
                gv = dec-math.fabs(glon)
            if (gv > +180.0):
                gv = gv - 360.0
            if (gv < -180.0):
                gv = gv + 360.0

        otime = time
        oalt = alt
        olat = glat
        olon = glon

        class RetObj:
            pass
        retobj = RetObj()
        retobj.dec = dec
        retobj.dip = dip
        retobj.ti = ti
        retobj.bh = bh
        retobj.bx = bx
        retobj.by = by
        retobj.bz = bz
        retobj.lat = dlat
        retobj.lon = dlon
        retobj.alt = h
        retobj.time = time
        retMag = np.matrix([retobj.bx, retobj.by, retobj.bz])
        retMag = retMag.transpose()
        #retFinal = np.matrix([retMag, retobj.bh, dec, retobj.dip, retobj.ti])
        # return retobj
        return retMag

    def __init__(self, wmm_filename=None):
        if not wmm_filename:
            wmm_filename = os.path.join(os.path.dirname(__file__), 'WMM.COF')
        wmm = []
        with open(wmm_filename) as wmm_file:
            for line in wmm_file:
                linevals = line.strip().split()
                if len(linevals) == 3:
                    self.epoch = float(linevals[0])
                    self.model = linevals[1]
                    self.modeldate = linevals[2]
                elif len(linevals) == 6:
                    linedict = {'n': int(float(linevals[0])),
                                'm': int(float(linevals[1])),
                                'gnm': float(linevals[2]),
                                'hnm': float(linevals[3]),
                                'dgnm': float(linevals[4]),
                                'dhnm': float(linevals[5])}
                    wmm.append(linedict)

        z = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
             0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.maxord = self.maxdeg = 12
        self.tc = [z[0:13], z[0:13], z[0:13], z[0:13], z[0:13], z[0:13],
                   z[0:13], z[0:13], z[0:13], z[0:13], z[0:13], z[0:13], z[0:13], z[0:13]]
        self.sp = z[0:14]
        self.cp = z[0:14]
        self.cp[0] = 1.0
        self.pp = z[0:13]
        self.pp[0] = 1.0
        self.p = [z[0:14], z[0:14], z[0:14], z[0:14], z[0:14], z[0:14], z[0:14],
                  z[0:14], z[0:14], z[0:14], z[0:14], z[0:14], z[0:14], z[0:14]]
        self.p[0][0] = 1.0
        self.dp = [z[0:13], z[0:13], z[0:13], z[0:13], z[0:13], z[0:13],
                   z[0:13], z[0:13], z[0:13], z[0:13], z[0:13], z[0:13], z[0:13], z[0:13]]
        self.a = 6378.137
        self.b = 6356.7523142
        self.re = 6371.2
        self.a2 = self.a*self.a
        self.b2 = self.b*self.b
        self.c2 = self.a2-self.b2
        self.a4 = self.a2*self.a2
        self.b4 = self.b2*self.b2
        self.c4 = self.a4 - self.b4

        self.c = [z[0:14], z[0:14], z[0:14], z[0:14], z[0:14], z[0:14], z[0:14],
                  z[0:14], z[0:14], z[0:14], z[0:14], z[0:14], z[0:14], z[0:14]]
        self.cd = [z[0:14], z[0:14], z[0:14], z[0:14], z[0:14], z[0:14],
                   z[0:14], z[0:14], z[0:14], z[0:14], z[0:14], z[0:14], z[0:14], z[0:14]]

        for wmmnm in wmm:
            m = wmmnm['m']
            n = wmmnm['n']
            gnm = wmmnm['gnm']
            hnm = wmmnm['hnm']
            dgnm = wmmnm['dgnm']
            dhnm = wmmnm['dhnm']
            if (m <= n):
                self.c[m][n] = gnm
                self.cd[m][n] = dgnm
                if (m != 0):
                    self.c[n][m-1] = hnm
                    self.cd[n][m-1] = dhnm

        # /* CONVERT SCHMIDT NORMALIZED GAUSS COEFFICIENTS TO UNNORMALIZED */
        self.snorm = [z[0:13], z[0:13], z[0:13], z[0:13], z[0:13], z[0:13],
                      z[0:13], z[0:13], z[0:13], z[0:13], z[0:13], z[0:13], z[0:13]]
        self.snorm[0][0] = 1.0
        self.k = [z[0:13], z[0:13], z[0:13], z[0:13], z[0:13], z[0:13],
                  z[0:13], z[0:13], z[0:13], z[0:13], z[0:13], z[0:13], z[0:13]]
        self.k[1][1] = 0.0
        self.fn = [0.0, 2.0, 3.0, 4.0, 5.0, 6.0,
                   7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0]
        self.fm = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0,
                   6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0]
        for n in range(1, self.maxord+1):
            self.snorm[0][n] = self.snorm[0][n-1]*(2.0*n-1)/n
            j = 2.0
            # for (m=0,D1=1,D2=(n-m+D1)/D1;D2>0;D2--,m+=D1):
            m = 0
            D1 = 1
            D2 = (n-m+D1)/D1
            while (D2 > 0):
                self.k[m][n] = (((n-1)*(n-1))-(m*m))/((2.0*n-1)*(2.0*n-3.0))
                if (m > 0):
                    flnmj = ((n-m+1.0)*j)/(n+m)
                    self.snorm[m][n] = self.snorm[m-1][n]*math.sqrt(flnmj)
                    j = 1.0
                    self.c[n][m-1] = self.snorm[m][n]*self.c[n][m-1]
                    self.cd[n][m-1] = self.snorm[m][n]*self.cd[n][m-1]
                self.c[m][n] = self.snorm[m][n]*self.c[m][n]
                self.cd[m][n] = self.snorm[m][n]*self.cd[m][n]
                D2 = D2-1
                m = m+D1


def decyear(date):
    def sinceEpoch(date):  # returns seconds since epoch
        return time.mktime(date.timetuple())
    s = sinceEpoch

    year = date.year
    startOfThisYear = datetime(year=year, month=1, day=1)
    startOfNextYear = datetime(year=year+1, month=1, day=1)

    yearElapsed = s(date) - s(startOfThisYear)
    yearDuration = s(startOfNextYear) - s(startOfThisYear)
    fraction = yearElapsed/yearDuration

    return date.year + fraction


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


def getDCM(bV, sV, bI, sI):
    bV = np.reshape(bV, (1, -1))/linalg.norm(bV)
    sV = np.reshape(sV, (1, -1))/linalg.norm(sV)  #
    bI = np.reshape(bI, (1, -1))/linalg.norm(bI)  #
    sI = np.reshape(sI, (1, -1))/linalg.norm(sI)  #

    vu2 = np.asmatrix(np.cross(bV, sV))
    vu2 = np.asmatrix(vu2/linalg.norm(vu2))
    vmV = np.hstack(
        (bV.getH(), vu2.getH(), np.asmatrix(np.cross(bV, vu2)).getH()))
    iu2 = np.asmatrix(np.cross(bI, sI))
    iu2 = np.asmatrix(iu2/linalg.norm(iu2))
    imV = np.hstack(
        (bI.getH(), iu2.getH(), np.asmatrix(np.cross(bI, iu2)).getH()))
    ivDCM = np.asmatrix(vmV)*np.asmatrix(imV).getH()
    return ivDCM


class KOE:
    GM = 3.986004418*(10**14)
    sma = 6778557  # meters
    ecc = 0.0001973
    incl = 51.6397*math.pi/180
    raan = 115.7654*math.pi/180
    argp = 211.4532*math.pi/180
    tran = 0*math.pi/180
    """
    #ISS KOE at an epoch of 2018/3/18 @ 12:00:00.000
    sma = 6789165.94
    ecc = 0.0018939
    incl = 51.58923
    raan = 349.09863 deg
    argp = 55.38890 deg
    tran = 318.52399 deg
    """


class sc:
    jd0 = utc2jul(datetime(2018, 11, 8, 12, 0, 0))
    inertia = np.diag([.0108, .0108, .0108])


"""""""""""""""""""""""
DRIVING THREAD
"""""""""""""""""""""""
# def listen():
#    while True:
epoch = datetime(2018, 11, 8, 12, 0, 0)  # datetime.utcnow()
sc.jd0 = utc2jul(epoch)
sc.inertia = np.diag([.0108, .0108, .0108])

# Orbital Properties
GM = 3.986004418*(10**14)
KOE = np.array([KOE.sma, KOE.ecc, KOE.incl, KOE.raan, KOE.argp, KOE.tran])
current_time = epoch
epoch = np.array([epoch.year, epoch.month, epoch.day, epoch.hour,
                  epoch.minute, epoch.second])
cart = kep2cart(KOE)
cartloc = np.array([cart[0, 0], cart[0, 1], cart[0, 2]])

# Magnetic Field Model
epochvec = jd2dvec(sc.jd0)
lla = np.array([5.335745187657780, -1.348386750055788e+02,
                3.968562753276266e+05*3.28084])  # CONVERT METERS TO FEET
#lla = np.array(gps.lat, gps.lon, gps.alt)
gm = wrldmagm("WMM.COF")
magECEF = gm.wrldmagm(lla[0], lla[1], lla[2],
                      decyear(datetime(2018, 1, 1)))
magECEF = np.squeeze(np.asarray(magECEF))
magECI = pymap3d.ecef2eci(magECEF, current_time)

# Initial CubeSat Attitude
#qtrue = [.5,.5,.5,.99];
#qtrue = [0.5435   -0.0028   -0.6124   -0.5741];

# THIS IS ALL SIMULATION DELETE THESE LINES IN FLIGHT CODE
qtrue = np.matrix([0, 0, math.sqrt(2)/2, math.sqrt(2)/2])
qtrue = qtrue/np.linalg.norm(qtrue)
qtrue = np.squeeze(np.asarray(qtrue))
DCMtrue = q2dcm(qtrue)

# Sensor Outputs
# [magTotal,~] = BDipole(cart,sc.jd0,[0;0;0]);

# BV AND SV ARE SIMULATION PARAMETERS; IN FLIGHT CODE WE TAKE IT FROM THE MAGNETOMETER
bI = 1.0*(10e-09) * magECI
bI = bI/np.linalg.norm(bI)
bI = np.asmatrix(bI)
bI = bI.getH()

sI = sun_vec(sc.jd0-utc2jul(datetime(1980, 1, 6, 0, 0, 0)))
sI = sI/np.linalg.norm(sI)

bV = DCMtrue*bI
bV = bV/np.linalg.norm(bV)
bV = np.asmatrix(bV)

sV = DCMtrue*sI
sV = sV/np.linalg.norm(sV)
sV = np.squeeze(np.asarray(sV))
tempsV = list()
for x in range(0, len(sV)):
    tempsV.append(np.trim_zeros(sV[x]))
sV = np.asmatrix(tempsV)

# Attitude properties
dcm = getDCM(bV, sV, bI, sI)
print(dcm)
"""
Still needs to be converted:
"""
"""
q = dcm2q(dcm)

#Control Torque Calculation
#qref = getqref(struct2array(KOE));
qref = [0,0,-sqrt(2)/2,sqrt(2)/2];
qerr = getqerr(q0,qref);
thetaerr = getthetaerr(qerr);
#ctcomm = -1*sim.gain*thetaerr-1*sim.rgain*(w0-sim.wref); #Expected control torque (row vector)
ctcomm = -1*sim.gain*thetaerr;
magdip = getMC(ctcomm',bV,sim.mmax,sim.mtrans); #Magnetic dipole in body frame
ctprod = cross(magdip,bV);
"""
# time.sleep(1);
