import serial
import os
import threading

from core.threadhandler import ThreadHandler

write_lock = threading.Lock()


def start(master, slave):
    global ser, ser_slave, ser_master, antenna_power, is_assigned, is_fixed, jobs, t3, t4, gpgga_time, bestxyz_time
    ser_master = master
    ser_slave = slave
    antenna_power = False
    is_assigned = False
    is_fixed = False
    gpgga_time = 0
    bestxyz_time = 0
    jobs = []

    ser = serial.Serial(os.ttyname(ser_master), 19200)
    t1 = ThreadHandler(target=listen, name="receive")
    t2 = ThreadHandler(target=respond, name="transmit")
    t3 = threading.Timer(float(gpgga_time), write_gpgga)
    t4 = threading.Timer(float(bestxyz_time), write_bestxyz)
    t1.start()
    t2.start()


def listen():
    while True:
        res = None
        with write_lock:
            while res is None:
                res = os.read(ser_master, 100)
        jobs.extend(res.decode("utf-8"))


def write_gpgga():
    with write_lock:
        ser.write("gpgga data")


def write_bestxyz():
    with write_lock:
        ser.write("bestxyz data")


def set_fix(val):
    global is_fixed
    is_fixed = val


def unlogall():
    global jobs
    # jobs = [jobs.remove(x) for x in jobs if "log" in x]
    for x in jobs:
        if "log" in x:
            jobs.remove(x)
    t3.cancel()
    t4.cancel()


def set_power(val):
    global antenna_power
    antenna_power = val


def set_assign(val):
    global is_assigned
    is_assigned = val


def start_gppga(interval):
    global t3
    t3 = threading.Timer(float(interval), write_gpgga)
    t3.start()


def start_bestxyz(interval):
    global t4
    t4 = threading.Timer(float(interval), write_bestxyz)
    t4.start()


def respond():
    while True:
        for j in jobs:
            if j == "unlogall":
                unlogall()
            elif "log" in j:
                if antenna_power and is_assigned and is_fixed:
                    if "gpgga" in j:
                        start_gppga(j[j.rfind(" ")+1:])
                    elif "bestxyz" in j:
                        start_bestxyz(j[j.rfind(" ")+1:])
            elif j == "FIX AUTO":
                set_fix(True)
            elif j == "ANTENNAPOWER ON":
                set_power(True)
            elif j == "ANTENNAPOWER OFF":
                set_power(False)
            elif j == "ASSIGNALL AUTO":
                set_assign(True)
            elif j == "UNASSIGNALL":
                set_assign(False)
