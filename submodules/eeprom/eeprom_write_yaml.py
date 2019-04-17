#!/usr/bin/python
# write 16-bit EEPROMs over I2C
import sys
import smbus
import time
import yaml

def write_yaml(address=0x50, filename="config.yaml"):
	with open(filename) as f:
		config = yaml.load(f)

	bus = smbus.SMBus(1)

	device_address = int(address)
	#data = sys.stdin.read()
	data = str(config)+"!"
	chunks = []
	i = 0
	while i * 16 < len(data):
		chunk = data[i * 16:(i + 1) * 16]
		print (write(bus, device_address, i * 16, chunk))
		time.sleep(0.1) # needs some time to finish write, or fails [Errno 5] Input/output error
		i += 1

def write(bus, device_address, memory_address, data):
	cmd = memory_address >> 8
	bytes = [memory_address & 0xff] + list(map(ord, data))
	print("writing to %.2x at %.4x bytes %d" % (device_address, memory_address, len(data)))
	print(bytes)
	return bus.write_i2c_block_data(device_address, cmd, bytes)

if __name__ == "__main__":
	write_yaml()
