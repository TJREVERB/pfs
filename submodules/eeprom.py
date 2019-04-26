import yaml
import sys
import smbus
import ast
import time


def remove_var(address=0x50, what)


data = read()
data = data[0:data.indexOf(
    what)]+data[data.indexOf("!", data.indexOf(what)+1)+1:len(data)]
write_var(0x50, data)


def write_var(address=0x50, what):
    device_address = int(address)
    data = read() + what + "!"
    chunks = []
    i = 0
    while i * 16 < len(data):
        chunk = data[i * 16:(i + 1) * 16]
        print(write(bus, device_address, i * 16, chunk))
        # needs some time to finish write, or fails [Errno 5] Input/output error
        time.sleep(0.1)
        i += 1


def start():
    global bus
    bus = smbus.SMBus(1)  # /dev/i2c-1
    make_file()


def store_yaml(address=0x50, filename="config.yaml"):
    write_yaml(address, filename)


def regen_yaml(address=0x50, size=1024):
    read(address, size)


def count():
    pass


def make_file():
    stream = open("new_yaml.yaml", "w")
    yaml.dump(read(), stream)
    print(yaml.dump(read()))


def read(address=0x50, size=130144, data_num=0):
    device_address = int(address)
    size = int(size)

    out = ''

    memory_address = 0
    bus.write_byte(device_address, memory_address >> 8)
    bus.write_byte(device_address, memory_address & 0xff)
    for i in range(0, size):
        byte = bus.read_byte(device_address)
        # byte2 = bus.read_i2c_block_data(device_address, i, 16)
        out = out + str(chr(byte))
    # out = out + str(list(map(chr, byte2)))
    if(data_num == 0):
        return ast.literal_eval(out[0:out.rfind("!")].replace("''", ""))
    return ast.literal_eval(out[0:StringUtils.ordinalIndexOf(out, "!", data_num)].replace("''", ""))


def write_yaml(address=0x50, filename="config.yaml"):
    with open(filename) as f:
        config = yaml.load(f)

    device_address = int(address)
    data = str(config) + "!"
    chunks = []
    i = 0
    while i * 16 < len(data):
        chunk = data[i * 16:(i + 1) * 16]
        print(write(bus, device_address, i * 16, chunk))
        # needs some time to finish write, or fails [Errno 5] Input/output error
        time.sleep(0.1)
        i += 1


def write(bus, device_address, memory_address, data):
    cmd = memory_address >> 8
    bytes = [memory_address & 0xff] + list(map(ord, data))
    print("writing to %.2x at %.4x bytes %d" %
          (device_address, memory_address, len(data)))
    print(bytes)
    return bus.write_i2c_block_data(device_address, cmd, bytes)
