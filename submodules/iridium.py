import threading
import serial
import time
import sys
import logging

debug = True

global ser


def sendCommand(cmd):
    if cmd[-1] != '\r\n':
        cmd += '\r\n'
    # if debug:
    # print("Sending command: {}".format(cmd))
    ser.write(cmd.encode('UTF-8'))
    ser.flush()
    cmd_echo = ser.readline()
    # if debug:
    # print("Echoed: " + cmd_echo.decode('UTF-8'))


def setup(port):
    global ser
    ser = serial.Serial(port=port, baudrate=19200, timeout=15)
    ser.flush()
    doTheOK()


def doTheOK():
    sendCommand("AT")
    ser.readline().decode('UTF-8')  # get the empty line
    resp = ser.readline().decode('UTF-8')
    # # print (resp)
    if 'OK' not in resp:
        # # print("Echo"+resp)
        exit(-1)

    # show signal quality
    sendCommand('AT+CSQ')
    ser.readline().decode('UTF-8')  # get the empty line
    resp = ser.readline().decode('UTF-8')
    ser.readline().decode('UTF-8')  # get the empty line
    ok = ser.readline().decode('UTF-8')  # get the 'OK'
    # # # print("resp: {}".format(repr(resp)))
    if 'OK' not in ok:
        # print('Unexpected "OK" response: ' + ok)
        exit(-1)
    sendCommand("AT+SBDMTA=0")
    # if debug:
    # print("Signal quality 0-5: " + resp)
    ser.write("AT+SBDREG? \r\n".encode('UTF-8'))
    while True:
        try:
            regStat = int(ser.readline().decode('UTF-8').split(":")[1])
            break
        except:
            continue
        break
    if regStat != 2:
        sendCommand("AT+SBDREG")


def on_Startup():
    argument = " "
    command = " "
    global port
    if len(sys.argv) > 1:
        port = sys.argv[1]
    else:
        port = '/dev/ttyUSB0'
    setup(port)

    # setup(port)
    # if debug:
    # # print("Connected to {}".format(ser.name))

    # clear everything in buffer
    # ser.reset_input_buffer()
    # ser.reset_output_buffer()
    # disable echo
    # sendCommand('ATE0', has_resp=True)


def listen():
    ser = serial.Serial(port=port, baudrate=19200, timeout=1)
    sendCommand("AT+SBDMTA=1")
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
                sendCommand("AT+SBDIXA")
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
            sendCommand("AT+SBDRT")
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
            # sendCommand("at+sbdmta=0")
        # ser.flush()
        # print("listening...")


def send(thingToSend):
    # try to send until it sends
    startTime = time.time()
    alert = 2
    while alert == 2:
        # signal = ser.readline().decode('UTF-8')#empty line
        # signal = ser.readline().decode('UTF-8')#empty line
        sendCommand("AT+CSQF")

        signal = ser.readline().decode('UTF-8')  # empty line
        signal = ser.readline().decode('UTF-8')
        # print("last known signal strength: "+signal)
        # prepare message
        sendCommand("AT+SBDWT=" + thingToSend)
        ok = ser.readline().decode('UTF-8')  # get the 'OK'
        ser.readline().decode('UTF-8')  # get the empty line

        # send message
        sendCommand("AT+SBDI")

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


on_Startup()
time.sleep(10)
send('hi')
