
#!/usr/bin/python
# read 16-bit EEPROMs over I2C. tested with 24FC512 and 24LC515

import sys
import smbus
bus = smbus.SMBus(1) # /dev/i2c-1

if len(sys.argv) < 3:
	sys.stderr.write("usage: %s device_address size > filename\n" % (sys.argv[0],))
	raise SystemExit

device_address = int(sys.argv[1], 16)
size = int(sys.argv[2])

memory_address = 0
bus.write_byte(device_address, memory_address >> 8)
bus.write_byte(device_address, memory_address & 0xff)
for i in range(0,size):
	byte = bus.read_byte(device_address)
	sys.stdout.write(chr(byte))
