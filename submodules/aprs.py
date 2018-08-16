import logging
import os
import time
from threading import Thread

import serial

import submodules.command_ingest as ci
from core import config

logger = logging.getLogger("APRS")
pausesend = False
sendbuffer = []
didigettelem = False
user = False
bperiod = 60


# This will send a message to the device
# It is equivalent to typing in putty
def send(msg):
    global sendbuffer
    msg = msg + "\r\n"
    sendbuffer = sendbuffer + [msg]
    # add the message to the end of sendbuffer


def sendloop():
    global sendbuffer, pausesend
    # THIS LINE IS NEEDED
    # IT IS THE EQUIVALENT OF PRESSING ENTER IN PUTTY

    # logger.debug("Hidylan")
    # print(msg)
    # print(bytes(msg,encoding="utf-8"))
    # ser.write(bytes(msg,encoding="utf-8"))
    # TURNS YOUR STRING INTO BYTES
    # NEEDED TO PROPERLY SEND OVER SERIAL
    while True:
        while len(sendbuffer) > 0:
            if pausesend:
                time.sleep(1)
                pausesend = False
            # CHECK IF THERE IS SOMETHING IN SENDBUFFER
            ser.write(sendbuffer[0].encode("utf-8"))
            logger.debug('SENT MESSAGE')
            # WRITE FIRST ELEMENT IN SENDBUFFER TO SERIAL
            sendbuffer = sendbuffer[1:]
            # DELETE FIRST ELEMENT IN SENDBUFFER
            time.sleep(1)
        time.sleep(1)


# THIS METHOD THREAD RUNS FOREVER ONCE STARTED
# AND PRINTS ANYTHING IT RECIEVES OVER THE SERIAL LINE
def dump():
    pass


def telemwatchdog():
    global didigettelem
    while True:
        time.sleep(70)
        if not didigettelem:
            logger.info("APRS IS DEAD DO SOMETHING")
        else:
            logger.debug("WATCHDOG PASS APRS")
        didigettelem = False


def listen():
    while True:
        # IF I GET SOMETHING OVER THE SERIAL LINE
        zz = ser.inWaiting()
        # READ THAT MANY BYTES
        rr = ser.read(size=zz)
        if zz > 0:
            time.sleep(.5)
            # CHECK AFTER .5 SECONDS, AND READ ANYTHING THAT GOT LEFT BEHIND
            zz = ser.inWaiting()
            rr += ser.read(size=zz)
            ci.dispatch_command(rr)
            # print(rr)
            # log('GOT: '+rr)
            # return (rr)
            # return rr


def keyin():
    global user
    while True:
        # GET INPUT FROM YOUR OWN TERMINAL
        # TRY input("shihaoiscoolforcommentingstuff") IF raw_input() doesn't work
        in1 = input("Type Command: ")
        if user:
            send("TJ" + in1 + chr(sum([ord(x) for x in "TJ" + in1]) % 128))
        else:
            send(in1)
            log_message('SENT: ' + in1)
        # FOR ANY NON APRS MODULES THE ABOVE "IF" LOGIC IS UN-NEEDED.
        # JUST USE SEND


# APRS ONLY
def beacon():
    while True:
        logger.info("SENT BEACON")
        btext = "HW"
        send(btext)
        log_message('BEACON: ' + btext)
        time.sleep(bperiod)


# ANYTHING IN HERE WILL BE EXECUTED ON STARTUP
def on_startup():
    global ser, logfile
    # Opens the serial port for all methods to use with 19200 baud
    ser = serial.Serial(config['aprs']['serial_port'], 19200)

    # Create all the background threads
    t1 = Thread(target=listen, args=(), daemon=True)
    t2 = Thread(target=sendloop, args=(), daemon=True)
    t3 = Thread(target=telemwatchdog, args=(), daemon=True)
    t4 = Thread(target=beacon, args=(), daemon=True)

    # Open the log file
    log_dir = os.path.join(config['core']['log_dir'], 'aprs')
    filename = 'aprs' + '-'.join([str(x) for x in time.localtime()[0:3]])
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    logfile = open(os.path.join(log_dir, filename + '.txt'), 'a+')

    # Mark the start of the log
    log_message('RUN@' + '-'.join([str(x) for x in time.localtime()[3:5]]))
    t3.daemon = True

    # Start the background threads
    t1.start()
    t2.start()
    t3.start()
    t4.start()


# HAVE THE 3 BELOW METHODS. SAY PASS IF YOU DONT KNOW WHAT TO PUT THERE YET
# THESE ARE IN REFERENCE TO POWER LEVELS. SHUT STUFF DOWN IF WE NEED TO GO TO
# EMERGYENCY MODE OR LOW POWER. ENTERING NORMAL MODE SHOULD TURN THEM BACK ON
def enter_normal_mode():
    global bperiod
    bperiod = 60


def enter_low_power_mode():
    global bperiod
    bperiod = 120


def enter_emergency_mode():
    pass


def log_message(msg):
    global logfile
    # Write to file
    logfile.write(msg + '\n')
    logfile.flush()


# Anything in here will execute if you run `python aprs_pi.py'
# it is the same as main in java
if __name__ == '__main__':
    # Calls the stuff to happen on startup
    on_startup()
    # This starts your thread to listen for keyboard input
    t5 = Thread(target=keyin, args=(), daemon=True)
    t5.start()
    # This loop is needed to keep your threads alive
    while True:
        time.sleep(1)
