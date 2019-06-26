import ast
import time

import smbus2 as smbus
import yaml


def clear(address):
    device_address = int(address)
    data = "."
    i = 0
    while i * 16 < size:
        chunk = "................"
        print(write(bus, device_address, i * 16, chunk))
        # needs some time to finish write, or fails [Errno 5] Input/output error
        time.sleep(0.1)
        i += 1


def remove_var(what, address=0x50):
    data = read()
    data = data[0:data.index(
        what)]+data[data.index("!", data.index(what)+1)+1:len(data)]
   # write(bus, 0x50, 0, data) TODO: Fix


def write_var(what, address=0x50):
    device_address = int(address)
    data = read() + "!" + what + "!"
    chunks = []
    i = 0
    while i * 16 < len(data):
        chunk = data[i * 16:(i + 1) * 16]
        print(write(bus, device_address, i * 16, chunk))
        # needs some time to finish write, or fails [Errno 5] Input/output error
        time.sleep(0.1)
        i += 1


def start():
    global size
    global bus
    size = 131072
    bus = smbus.SMBus(1)  # /dev/i2c-1
   # make_file()


def store_yaml(address=0x50, filename="config.yaml"):
    write_yaml(address, filename)


def regen_yaml(address=0x50, size=1024):
    read(address, size)


def count():
    pass


def make_file():
    stream = open("new_yaml.yaml", "w")
    #yaml.dump(read(), stream)
    yaml.dump(ast.literal_eval(read(0x50, 8192, 1)), stream)


def read(address=0x50, size=8192, data_num=0, s=""):
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
    if data_num == 0:
        # return out[0:out.rfind("!")].replace("''", "")
        return out
    if(data_num == 1):
        return out[0:iter_find(out, "!")[0]].replace("''", "")
    return out[iter_find(out, "!")[data_num-2]+1:iter_find(out, "!")[data_num-1]].replace("''", "")


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
    bytes = [memory_address & 0xff] + data
    # print("writing to %.2x at %.4x bytes %d" %
    #      (device_address, memory_address, len(data)))
   # print(bytes)
    return bus.write_i2c_block_data(device_address, cmd, bytes)


def iter_find(haystack, needle):
    return [i for i in range(0, len(haystack)) if haystack[i:].startswith(needle)]
