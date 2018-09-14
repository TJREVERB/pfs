import logging
import os
import time
from threading import Thread
from typing import Union

import serial

import submodules.command_ingest as ci
from core import config
# Initalize global variables
from submodules import command_ingest
from submodules.command_ingest import logger, dispatch

logger = logging.getLogger("APRS")
pause_sending = False
send_buffer = []
beacon_seen = False
last_telem_time = time.time()
last_message_time = time.time()

user = False
bperiod = 60
ser: Union[serial.Serial, None] = None


# Enqueue a message to be sent
def enqueue(msg):
    global send_buffer
    msg = msg + "\r\n"
    send_buffer += [msg]


# Send all messages in the queue
def send_loop():
    global send_buffer
    while True:
        while len(send_buffer) > 0:
            # This waits until `message_spacing` seconds after the last recieved message
            while time.time() - last_message_time < config['aprs']['message_spacing']:
                time.sleep(1)
            # Send the message
            ser.write(send_buffer[0].encode("utf-8"))
            # Remove message from queue
            send_buffer = send_buffer[1:]
            time.sleep(1)
        time.sleep(1)


def telemetry_watchdog():
    while True:
        time.sleep(config['aprs']['telem_timeout'])
        if time.time() - last_telem_time > config['aprs']['telem_timeout']:
            logger.error("APRS IS DEAD DO SOMETHING")
            # TODO: do reset via EPS
        else:
            logger.debug("Watchdog pass APRS")


def listen():
<<<<<<< HEAD
    while (True):
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
    while (True):
        # GET INPUT FROM YOUR OWN TERMINAL
        # TRY input("shihaoiscoolforcommentingstuff") IF raw_input() doesn't work
        in1 = input("Type Command: ")
        if (user):
            send("TJ" + in1 + chr(sum([ord(x) for x in "TJ" + in1]) % 26+65))
        else:
            send(in1)
            log('SENT: ' + in1)
        # FOR ANY NON APRS MODULES THE ABOVE "IF" LOGIC IS UN-NEEDED.
        # JUST USE SEND
=======
    while True:
        # Read in a full message from serial
        line = ser.readline()
        # Dispatch command
        parse_aprs_packet(line)
>>>>>>> c076dd50ad18ab9d1eec25c1caea4fc41ec715e6


def parse_aprs_packet(packet):
    raw_packet = str(packet)
    logger.info("From APRS: " + raw_packet)
    header_index = raw_packet.find(':')
    if header_index == -1:
        logger.info("Incomplete header")
        return
    header = raw_packet[:header_index]
    logger.info("header: " + header)
    data = raw_packet[header_index + 1:]

    if len(data) == 0:
        logger.debug("Empty body")
        return

    logger.debug("Body: " + data)
    command_ingest.dispatch(data)


# Method that is called upon application startup.
def on_startup():
    global ser, logfile
    # Opens the serial port for all methods to use with 19200 baud
    ser = serial.Serial(config['aprs']['serial_port'], 19200)

    # Create all the background threads
    t1 = Thread(target=listen, args=(), daemon=True)
    t2 = Thread(target=send_loop, args=(), daemon=True)
    t3 = Thread(target=telemetry_watchdog, args=(), daemon=True)

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


# Have the 3 below methods. Say pass if you dont know what to put there yet
# these are in reference to power levels. Shut stuff down if we need to go to
# emergency mode or low power. Entering normal mode should turn them back on
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

