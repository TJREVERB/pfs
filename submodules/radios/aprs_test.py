from pty import openpty
from os import ttyname, read, write

from .aprs import APRS

config = {
    "aprs": {
        "serial_port": ""
    }
}


class FakeTelemetry:
    def __init__(self, expected_data):
        self.expected_data = expected_data

    def enqueue(self, message):
        print(f"messaage: {list(message)}, ed: {list(self.expected_data)}")
        assert self.expected_data == message


def start_fake(expected_data=""):
    """
    Common code to all test cases (opens a fake serial port and creates an APRS test object)
    :param expected_data: If testing GS to pFS, what str APRS is expected to pass to Telemetry
    :return: tuple: (APRS object, master serial device)
    """
    master, slave = openpty()
    port_name = ttyname(slave)
    config["aprs"]["serial_port"] = port_name

    modules = {
        "telemetry": FakeTelemetry(expected_data)
    }
    aprs = APRS(config)
    aprs.set_modules(modules)
    return aprs, master


def test_normal_str():
    test_str = "header:content\n"
    content = "content\n"
    aprs, master = start_fake(content)
    aprs.start()

    for c in test_str:
        b = c.encode("utf-8")
        write(master, b)

def run_tests():
    test_normal_str()
