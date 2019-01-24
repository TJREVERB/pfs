import threading
from functools import partial

import serial
import time
import sys
import logging

from core import config
from . import command_ingest
from . import eps
from .command_ingest import command
from helpers.threadhandler import ThreadHandler
from helpers.helpers import is_simulate

debug = True

global ser

# Initialize global variables
logger = logging.getLogger("IRIDIUM")

def write_to_serial(cmd):
    if cmd[-1] != '\r\n':
        cmd += '\r\n'
    # if debug:
    # print("Sending command: {}".format(cmd))
    ser.write(cmd.encode('UTF-8'))
    ser.flush()
    cmd_echo = ser.readline()
    # if debug:
    # print("Echoed: " + cmd_echo.decode('UTF-8'))


def check():
    write_to_serial("AT")

    ser.readline().decode('UTF-8')  # get the empty line
    resp = ser.readline().decode('UTF-8')
    # # print (resp)
    if 'OK' not in resp:
        # # print("Echo"+resp)
        exit(-1)

    # show signal quality
    write_to_serial('AT+CSQ')
    ser.readline().decode('UTF-8')  # get the empty line
    resp = ser.readline().decode('UTF-8')
    ser.readline().decode('UTF-8')  # get the empty line
    ok = ser.readline().decode('UTF-8')  # get the 'OK'
    # # # print("resp: {}".format(repr(resp)))
    if 'OK' not in ok:
        # print('Unexpected "OK" response: ' + ok)
        exit(-1)
    write_to_serial("AT+SBDMTA=0")
    # if debug:
    # print("Signal quality 0-5: " + resp)
    ser.write("AT+SBDREG? \r\n".encode('UTF-8'))
    while True:
        try:
            regStat = int(ser.readline().decode('UTF-8').split(":")[1])
            break
        except:
            continue
    if regStat != 2:
        write_to_serial("AT+SBDREG")


def listen():
    write_to_serial("AT+SBDMTA=1")
    signalStrength = 0
    ringSetup = 0
    iteration = 0
    while ringSetup != 2:
        print("Just inside ring setup loop")
        ring = ser.readline().decode('UTF-8')
        print(ring)
        print("if SBDRING next")
        if "SBDRING" in ring:
            bytesLeft = 1
            ser.timeout = 120
            while bytesLeft != 0:
                print("checking bytes left")
                write_to_serial("AT+SBDIXA")
                resp = "A"
                while len(resp) < 2:
                    print("response length loop")
                    test = ser.readline().decode('UTF-8')
                    # print("Response before Splitting: "+test)
                    resp = test.split(': ')
                # print("Response after splitting:  "+resp[1]+" 0 "+resp[0]+" END")
                try:
                    print("splitting response")
                    resp = resp[1].split(', ')
                except:
                    print("index out of bounds exception \r\n closing program")
                    exit(-1)
                bytesLeft = int(resp[0])
                # print("split response: "+resp[1])
                # bytesLeft = 0
            write_to_serial("AT+SBDRT")
            print("About to show message")
            while True:
                try:
                    print(ser.readline().decode('UTF-8').split(":")[1])

                    print("done")
                    break
                except:
                    continue
            ringSetup = 0
            # print(ser.readline().decode('UTF-8'))
            # print(ser.readline().decode('UTF-8'))
            # print(ser.readline().decode('UTF-8'))
            # print(ser.readline().decode('UTF-8'))
            # print(ser.readline().decode('UTF-8'))
            # print(ser.readline().decode('UTF-8'))
            # write_to_serial("at+sbdmta=0")
        # ser.flush()
        # print("listening...")


def send(message):
    # try to send until it sends
    startTime = time.time()
    alert = 2
    while alert == 2:
        # signal = ser.readline().decode('UTF-8')#empty line
        # signal = ser.readline().decode('UTF-8')#empty line
        write_to_serial("AT+CSQF")

        signal = ser.readline().decode('UTF-8')  # empty line
        signal = ser.readline().decode('UTF-8')
        # print("last known signal strength: "+signal)
        # prepare message
        write_to_serial("AT+SBDWT=" + message)
        ok = ser.readline().decode('UTF-8')  # get the 'OK'
        ser.readline().decode('UTF-8')  # get the empty line

        # send message
        write_to_serial("AT+SBDI")

        resp = ser.readline().decode('UTF-8')  # get the empty line
        resp = resp.replace(",", " ").split(" ")
        startTime = time.time()
        currTime = startTime

        # signal = ser.readline().decode('UTF-8')#empty line
        # signal = ser.readline().decode('UTF-8')#empty line
        while len(resp) > 0 and len(resp) <= 2:
            # # print(resp)
            resp = ser.readline().decode('UTF-8')
            resp = resp.replace(",", " ").split(" ")
            curTime = time.time()
            if (curTime - startTime) > 30:
                # print("time out moving on")
                break
        # get the rsp

        #  if debug:
        # print("resp: {}"t )
        try:
            # print("*" + str(resp))
            alert = int(resp[1])
            # print(alert)
        except:
            # print("***exception thrown")
            continue

        # if debug:
        # print("alert: {}".format(alert))
    exit(-1)


def on_startup():
    global ser

    # Opens the serial port for all methods to use with 19200 baud
    ser = serial.Serial(config['iridium']['serial_port'], baudrate=19200, timeout=15)
    ser.flush()

    # Create all the background threads
    t1 = ThreadHandler(target=partial(listen), name="iridium-listen", parent_logger=logger)

    check()

    # Start the threads
    t1.start()

    time.sleep(1)
    send("TEST")
