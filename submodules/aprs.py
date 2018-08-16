import logging
import os
import time
from threading import Thread
from typing import Union

import serial

import submodules.command_ingest as ci
from core import config

logger = logging.getLogger("APRS")
pause_sending = False
send_buffer = []
beacon_seen = False
last_telem_time = time.time()

user = False
bperiod = 60
ser: Union[serial.Serial, None] = None


# This will send a message to the device
# It is equivalent to typing in putty
def send(msg):
    global send_buffer
    msg = msg + "\r\n"
    send_buffer = send_buffer + [msg]
    # add the message to the end of sendbuffer


def sendloop():
    global send_buffer, pause_sending
    # THIS LINE IS NEEDED
    # IT IS THE EQUIVALENT OF PRESSING ENTER IN PUTTY

    # logger.debug("Hidylan")
    # print(msg)
    # print(bytes(msg,encoding="utf-8"))
    # ser.write(bytes(msg,encoding="utf-8"))
    # TURNS YOUR STRING INTO BYTES
    # NEEDED TO PROPERLY SEND OVER SERIAL
    while True:
        while len(send_buffer) > 0:
            if pause_sending:
                time.sleep(1)
                pause_sending = False
            # CHECK IF THERE IS SOMETHING IN SENDBUFFER
            ser.write(send_buffer[0].encode("utf-8"))
            logger.debug('SENT MESSAGE')
            # WRITE FIRST ELEMENT IN SENDBUFFER TO SERIAL
            send_buffer = send_buffer[1:]
            # DELETE FIRST ELEMENT IN SENDBUFFER
            time.sleep(1)
        time.sleep(1)


# This method thread runs forever once started
# and prints anything it recieves over the serial line
def dump():
    pass


def telemetry_watchdog():
    while True:
        time.sleep(config['aprs']['telem_timeout'])
        if time.time() - last_telem_time > config['aprs']['telem_timeout']:
            logger.error("APRS IS DEAD DO SOMETHING")
            # do reset via EPS
        else:
            logger.debug("Watchdog pass APRS")


def listen():
    while True:
        # Read in a full message from serial
        line = ser.readline()
        # Dispatch command
        ci.parse_aprs_packet(line)


def key_input():
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
    t3 = Thread(target=telemetry_watchdog, args=(), daemon=True)
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
    # t4.start()


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
    t5 = Thread(target=key_input, args=(), daemon=True)
    t5.start()
    # This loop is needed to keep your threads alive
    while True:
        time.sleep(1)
