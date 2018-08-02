#YOU NEED TO RUN pip install pyserial and pip install logging
#TO HAVE ACCESS TO THE BELOW MODULES. DO THAT IN POWERSHELL OR CMDER OR BASH
#CONTACT SHIHAO OR DYLAN IF YOU HAVE questions
#DO NOT MODIFY THIS FILE, main.py or config.yaml WITHOUT MY PERMISSION

import serial
import time
import sys
import logging
#from core import config
#import submodules.command_ingest as ci
#from submodules.command_ingest import piprint
#import command_ingest as ci
#from submodules import command_ingest as ci

#THIS IMPORTS ALL SUBMODULES
from submodules import *
#IMPORT THREADING
from threading import Thread
#from core import config

#THIS IS FOR APRS ONLY:

#THIS WILL SEND A MESSAGE TO THE DEVICE
#IT IS EQUIVALENT TO TYPING IN PUTTY
def send(msg):
    #THIS LINE IS NEEDED
    #IT IS THE EQUIVALENT OF PRESSING ENTER IN PUTTY
    msg = msg + "\r\n"
    #logging.debug("Hidylan")
    #print(msg)
    #print(bytes(msg,encoding="utf-8"))
    #ser.write(bytes(msg,encoding="utf-8"))
    #TURNS YOUR STRING INTO BYTES
    #NEEDED TO PROPERLY SEND OVER SERIAL
    ser.write(msg.encode("utf-8"))
#THIS METHOD THREAD RUNS FOREVER ONCE STARTED
#AND PRINTS ANYTHING IT RECIEVES OVER THE SERIAL LINE
def listen():
    print("START LISTENING")
    while(True):
        #IF I GET SOMETHING OVER THE SERIAL LINE
        zz = ser.inWaiting()
        #READ THAT MANY BYTES
        #print(zz)
        rr = ser.read(size = zz)
        #print(rr)
        if zz > 0:
            #print('presleep')
            time.sleep(.5)
            #print('postsleep')
            #CHECK AFTER .5 SECONDS, AND READ ANYTHING THAT GOT LEFT BEHIND
            zz = ser.inWaiting()
            rr += ser.read(size = zz)
            print(rr)
            #log('GOT: '+rr)
            #return (rr)
            #return rr

def keyin():
    global user
    while(True):
        #GET INPUT FROM YOUR OWN TERMINAL
        #TRY input("shihaoiscoolforcommentingstuff") IF raw_input() doesn't work
        in1 = input("Type Command: ")
        if(user):
            send("TJ" + in1 + chr(sum([ord(x) for x in "TJ"+in1])%128))
        else:
            send(in1)
            log('SENT: '+in1)
        #FOR ANY NON APRS MODULES THE ABOVE "IF" LOGIC IS UN-NEEDED.
        #JUST USE SEND

#APRS ONLY
def beacon():
    global bperiod
    while(True):

        btext = "HELLO WORLD I AM FROMETH TJ"
        send(btext)
        log('BEACON: '+btext)
        time.sleep(bperiod)


#ANYTHING IN HERE WILL BE EXECUTED ON STARTUP
def on_startup():
    #GLOBAL VARIABLES ARE NEEDED IF YOU "CREATE" VARIABLES WITHIN THIS METHOD
    #AND ACCESS THEM ELSEWHERE
    global bperiod, t1, ser, logfile, user
    user = False
    bperiod = 60
    #serialPort = config['aprs']['serial_port']
    #REPLACE WITH COMx IF ON WINDOWS
    #REPLACE WITH /dev/ttyUSBx if 1 DOESNT WORK
    serialPort = "/dev/ttyS1"
    #OPENS THE SERIAL PORT FOR ALL METHODS TO USE WITH 19200 BAUD
    ser = serial.Serial(serialPort, 19200)
    #CREATES A THREAD THAT RUNS THE LISTEN METHOD
    t1 = Thread(target=listen, args=())
    t1.daemon = True
    t1.start()

    #logging.debug("Test")
    #logging.debug(time.localtime())
    #print(time.localtime()[0])
    #TEMP LOCAL TIME FOR REFERENCING LATER TO CREATE NAME
    tlt = time.localtime()
    #SET FILENAME WITH YEAR-MONTH-DAY
    filename = 'aprs'+'-'.join([str(x) for x in tlt[0:3]])
    #OPEN FILE
    logfile = open('/root/TJREVERB/pFS/submodules/logs/aprs/'+filename+'.txt','a+')
    #USE LOG FUNCTION TO MARK START
    log('RUN@'+'-'.join([str(x) for x in tlt[3:5]]))
    t3 = Thread(target=beacon, args=())
    t3.daemon = True
    t3.start()
#HAVE THE 3 BELOW METHODS. SAY PASS IF YOU DONT KNOW WHAT TO PUT THERE YET
#THESE ARE IN REFERENCE TO POWER LEVELS. SHUT STUFF DOWN IF WE NEED TO GO TO
#EMERGYENCY MODE OR LOW POWER. ENTERING NORMAL MODE SHOULD TURN THEM BACK ON
def enter_normal_mode():
    global bperiod
    bperiod = 60

def enter_low_power_mode():
    global bperiod
    bperiod = 120

def enter_emergency_mode():
    pass

def log(msg):
    global logfile
    #WRITE TO FILE
    logfile.write(msg+'\n')
    #SAVE CHANGES TO FILE
    logfile.flush()
#ANYTHING IN HERE WILL EXECUTE IF YOU RUN python aprs_pi.py
#IT IS THE SAME AS MAIN IN JAVA
if __name__ == '__main__':
    #CALLS THE STUFF TO HAPPEN ON STARTUP
    on_startup()
    #serialPort = sys.argv[1]
    #ser = serial.Serial(serialPort, 19200)
    #THIS STARTS YOUR THREAD TO LISTEN FOR KEYBOARD INPUT
    t2 = Thread(target=keyin, args=())
    t2.daemon = True
    t2.start()
    #THIS LOOP IS NEEDED TO KEEP YOUR THREADS ALIVE
    while True:
        time.sleep(1)
