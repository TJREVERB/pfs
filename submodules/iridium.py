import sys
import serial
import time
import os
import logging
from collections import deque
import threading


debug = True
global ser

d = deque('')

sys.path.append(os.path.abspath("/home/pi/iridium-jacob"))
from iridiumNotTestog import *


# Placeholder values for `telemetry.py`
total_received_ph = 100
success_checksum_ph = 60
fail_checksum_ph = 40
sent_messages_ph = 50


def enqueue(message):
	d.append(message)
	threading.thread(target=check_d).start()

def check_d():
	on_Startup()
	while len(d)>0:
		send(d.popleft())