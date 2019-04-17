#!/usr/bin/python
# read 16-bit EEPROMs over I2C. tested with 24FC512 and 24LC515

import sys
import smbus
import ast
bus = smbus.SMBus(1) # /dev/i2c-1
def read_yaml(address=0x50, size=1024):
	device_address = int(address)
	size = int(size)

	out = ''

	memory_address = 0
	bus.write_byte(device_address, memory_address >> 8)
	bus.write_byte(device_address, memory_address & 0xff)
	for i in range(0, size):
		byte = bus.read_byte(device_address)
		#byte2 = bus.read_i2c_block_data(device_address, i, 16)
		out = out + str(chr(byte))
		#out = out + str(list(map(chr, byte2)))

	return(ast.literal_eval(out[0:out.index("!")].replace("''", "")))

if __name__== "__main__":
	read_yaml()
