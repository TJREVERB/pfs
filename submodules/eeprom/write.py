#!/usr/bin/python
# write 16-bit EEPROMs over I2C
import sys
import smbus
import time

bus = smbus.SMBus(1)

if len(sys.argv) < 2:
	print("usage: %s device-address\n" % (sys.argv[0],))
	raise (SystemExit)

device_address = int(sys.argv[1], 16)
data = sys.stdin.read()

def write(device_address, memory_address, data):
	cmd = memory_address >> 8
	bytes = [memory_address & 0xff] + list(map(ord, data))
	print ("writing to %.2x at %.4x bytes %d" % (device_address, memory_address, len(data)))
	print(bytes)
	return bus.write_i2c_block_data(device_address, cmd, bytes)

chunks = []
i = 0
while i * 16 < len(data):
	chunk = data[i * 16:(i + 1) * 16]

	print (write(device_address, i * 16, chunk))
	time.sleep(0.1) # needs some time to finish write, or fails [Errno 5] Input/output error

	i += 1
