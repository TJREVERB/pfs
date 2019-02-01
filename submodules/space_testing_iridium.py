import threading
import serial
import time
import logging

debug = True

global ser

# Initialize global variables
logger = logging.getLogger("IRIDIUM")

def write_to_serial(cmd):
    if cmd[-1] != '\r\n':
        cmd += '\r\n'

    ser.write(cmd.encode('UTF-8'))
    ser.flush()
    cmd_echo = ser.readline()


def check():
    write_to_serial("AT")

    ser.readline().decode('UTF-8')  # Get the empty line
    resp = ser.readline().decode('UTF-8')
    if 'OK' not in resp:
        exit(-1)

    # show signal quality
    write_to_serial('AT+CSQ')
    ser.readline().decode('UTF-8')  # get the empty line
    resp = ser.readline().decode('UTF-8')
    ser.readline().decode('UTF-8')  # get the empty line
    ok = ser.readline().decode('UTF-8')  # get the 'OK'
    if 'OK' not in ok:
        exit(-1)
    write_to_serial("AT+SBDMTA=0")

    ser.write("AT+SBDREG? \r\n".encode('UTF-8'))
    while True:
        try:
            regStat = int(ser.readline().decode('UTF-8').split(":")[1])
            break
        except:
            continue
    if regStat != 2:
        write_to_serial("AT+SBDREG")


def send(message):
    # Try to send until it sends
    startTime = time.time()
    alert = 2
    while alert == 2:
        write_to_serial("AT+CSQF")

        signal = ser.readline().decode('UTF-8')  # empty line
        signal = ser.readline().decode('UTF-8')

        # Prepare message
        write_to_serial("AT+SBDWT=" + message)
        ok = ser.readline().decode('UTF-8')  # Get the 'OK'
        ser.readline().decode('UTF-8')  # Get the empty line

        # send message
        write_to_serial("AT+SBDI")

        resp = ser.readline().decode('UTF-8')  # Get the empty line
        resp = resp.replace(",", " ").split(" ")
        startTime = time.time()
        currTime = startTime

        while len(resp) > 0 and len(resp) <= 2:
            resp = ser.readline().decode('UTF-8')
            resp = resp.replace(",", " ").split(" ")
            curTime = time.time()
            if (curTime - startTime) > 30:
                break
        try:
            alert = int(resp[1])
        except:
            continue

    exit(-1)


def on_startup():
    global ser

    # Opens the serial port for all methods to use with 19200 baud
    ser = serial.Serial(config['iridium']['serial_port'], baudrate=19200, timeout=15)
    check()
    time.sleep(5)
    write_to_serial("AT")
    ser.readline().decode('UTF-8')
    ser.readline().decode('UTF-8')
    ser.readline().decode('UTF-8')
    ser.readline().decode('UTF-8')
    ser.readline().decode('UTF-8')