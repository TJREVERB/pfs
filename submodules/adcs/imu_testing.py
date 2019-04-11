#input: some object gyrodata from IMU
#square each value to get

from imu import gyr
import imu

gyrodata = imu.get_g()

threshold = 2500



def check_detumble(gyrodata):
    f = open("out.txt", "a")
    abs_gyro_square = gyrodata[0]**2 + gyrodata[1]**2 + gyrodata[2]**2
    f.write(abs_gyro_square)
    print(abs_gyro_square)
    if abs_gyro_square < threshold:
        return True
    else:
        return False
    f.close()

def imu_detumbled(gyrodata):
    while not check_detumble(gyrodata):
        continue
    print("detumbled")
