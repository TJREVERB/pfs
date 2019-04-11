from pathlib import Path
from datetime import datetime
import math
from decimal import Decimal

from core import load_config


def checksum(line):
    hey = ''.join(filter(lambda x: x.isdigit()
                         or x == "-", line)).replace(" ", "")
    hey2 = list(hey)
    b = 0
    for a in hey2:
        if(a == "-"):
            b = b+1
        elif(int(a) < 10):
            b = b+int(a)
    return b % 10


def propagate(poskep, lastmeanmot, lastmeananom, lasttime, revnum):
    GM = 3.986004418*(10**14)
    file = open((Path(__file__).parent.resolve() / "tjreverb_tle.txt"), "r")
    lines = file.readlines()
    eachline = list()
    for line in lines:
        eachline.append(line.split())
    d = poskep[0]
    # print(eachline[1][3])
    edays = str(round((d-datetime(datetime.utcnow().year, 1, 1, 0)
                       ).total_seconds()/(24*60*60)+1, 8))
    parts = edays.split(".")
    parts[0] = parts[0].rjust(3, '0')
    parts[1] = '{:.8f}'.format(float("."+parts[1]))
    # print(parts[0]+"."+parts[1].split(".")[1])
    eachline[1][3] = str(d.strftime("%y")) + parts[0] + \
        "."+parts[1].split(".")[1]
    # print(eachline[1][3])

    i = str(round(poskep[3], 4)).split(".")
    eachline[2][2] = i[0].rjust(3, " ") + "." + i[1].ljust(4, '0')
    # print(eachline[2][2])

    raan = str(round(poskep[4], 4)).split(".")
    eachline[2][3] = raan[0].rjust(3, " ") + "." + raan[1].ljust(4, '0')
    # print(eachline[2][3])

    e = str(round(poskep[2], 7)).split(".")
    eachline[2][4] = e[1].rjust(7, '0')
    # print(eachline[2][4])

    argp = str(round(poskep[5], 4)).split(".")
    eachline[2][5] = argp[0].rjust(3, " ") + "." + argp[1].ljust(4, '0')
    # print(eachline[2][5])

    alt = 400  #TODO: gps alt
    meanmot = (GM/((alt+6378000)**3))**(1/2)/(2*math.pi)*(24*60*60)  # gps alt
    meanmot = str(round(meanmot, 8)).split(".")
    meanmot = meanmot[0].rjust(2, " ") + "." + \
        str(round(int(meanmot[1]), 8)).ljust(8, '0')
    m1 = meanmot
    meanmot = float(meanmot)

    #E = (float)(2*math.atan(math.tan(poskep[6]/2)/((1+poskep[2])/(1-poskep[2])**(1/2))))
    E = 2*math.atan2(math.tan((poskep[6]/180*math.pi)/2),
                     math.sqrt((1+poskep[2])/(1-poskep[2])))
    E = (E + 2*math.pi) % (2*math.pi)  # make sure E is positive
    meananom = E - poskep[2]*math.sin(E)  # meananomaly = Eanom - e*sin(Eanom)
    meananom = meananom/math.pi*180  # convert to degrees
    #print (E)
    eachline[2][6] = str(meananom).lstrip('0').split(".")[0].rjust(
        3, " ") + "." + str(round(meananom, 4)).split(".")[1].ljust(4, '0')
    # TODO: write new mean anomaly, last year, and last day to config yaml file
    # print(eachline[2][6])

    firstd = (meanmot - lastmeanmot)/((poskep[0]-lasttime).total_seconds()/(60*60*24))
    firstd = firstd/2  # apparently tle is half of this
    # TODO: write meanmot to yaml
    randomsign = ""
    if(str(firstd) == "-"):
        randomsign = "-"
    eachline[1][4] = randomsign+str(firstd).lstrip('-').lstrip('0').split(
        ".")[0].rjust(1, ' ')+"."+str(round(firstd, 8)).split(".")[1].ljust(8, '0')
    # print(eachline[1][4])

    eachline[1][5] = " 00000-0"
    #print (eachline[1][5])

    bstar = "{:.5E}".format(Decimal(str(poskep[7]))).split("E")
    bstar[0] = bstar[0].replace(".", "")
    bstar[1] = str(int(bstar[1])+1)
    eachline[1][6] = " "+bstar[0][0:5]+bstar[1]

    eachline[1][7] = "0"
    #print (eachline[1][7])

    strrevnum = str(revnum)  # test value

    eachline[2][7] = m1+strrevnum.rjust(5, '0')
    # every time mean anomaly is 0 update yamlrevnum+1
    # print(eachline[2][7])
    lines = [eachline[1], eachline[2]]

    c1 = " 999"+str(checksum(lines[0][:-1]))
    eachline[1][8] = c1
    # print(eachline[1][8])

    c2 = str(checksum(lines[1]))
    eachline[2][7] = eachline[2][7]+c2
    # print(eachline[2][7])

    # print(eachline[2])
    # print(eachline)
    eachline[1][2] = eachline[1][2]+"  "
    lines = [eachline[1], eachline[2]]
    out = ""
    for q in lines:
        for p in q:
            out = out+p+" "
        out = out + "\n"
    file.close()
    return(out, meanmot, meananom, poskep[0])
    #upfile = open("tjreverb_tle.txt","w")
    # upfile.write(out)
    # upfile.close()

#propagate([datetime.utcnow(), 4344402.262071658,  0.0008799, 3.731724069345286, 1.0714496051147666, 1.8057985603867024, 270, 6.8825e-05])
