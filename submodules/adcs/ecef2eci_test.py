import pymap3d
from datetime import datetime
import numpy as np

retMag = np.matrix([28281.43702501, 4528.35388786, 8781.37008566])
print(retMag)
retMag = np.squeeze(np.asarray(retMag))
print(retMag)

magECI = pymap3d.ecef2eci(retMag, datetime(2018, 11, 8, 12, 0, 0))
print(magECI)

teams_list = ["Man Utd", "Man City", "T Hotspur"]
data = np.array([[1, 2, 1],
                 [0, 1, 0],
                 [2, 4, 2]])
row_format = "{:>15}" * (len(teams_list) + 1)
print(row_format.format("", *teams_list))
for team, row in zip(teams_list, data):
    print(row_format.format(team, *row))
