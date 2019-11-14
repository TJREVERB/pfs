from pty import openpty
from os import ttyname, read, write

from .aprs import APRS

config = {
    "aprs": {
        "serial_port": ""
    }
}

WORDS = ["Wood", "Low hanging FrUit", "documentation"]


class FakeTelemetry:
    def __init__(self, expected_data):
        self.expected_data = expected_data

    def enqueue(self, message):
        _assert = self.expected_data == message
        if not _assert:
            print(f"received: {list(message)}, expected: {list(self.expected_data)}")
        assert _assert


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


def test_write(test_str, content):
    aprs, master = start_fake(content)
    aprs.start()

    for c in test_str:
        b = c.encode("utf-8")
        write(master, b)


def test_with_header():
    for word in WORDS:
        test_str = f"header:{word}\n"
        content = f"{word}\n"
        test_write(test_str, content)


def test_with_no_header():
    print(f"Expect {len(WORDS)} `Incomplete APRS header!`")
    for word in WORDS:
        test_str = f"{word}\n"
        content = f"{word}\n"
        test_write(test_str, content)


def test_long_str():
    test_str = f"header:{'182nzfei92' * 5000}\n"
    content = '182nzfei92' * 5000 + "\n"
    test_write(test_str, content)


def test_short_str():
    test_str = f"header:i\n"
    content = "i\n"
    test_write(test_str, content)


def test_empty_str():
    test_str = "header:\n"
    content = "\n"
    test_write(test_str, content)


def test_spaces():
    test_str = "header:        \n"
    content = "        \n"
    test_write(test_str, content)


def test_escape_chars():
    test_str = "header:\t\r\t\a\n"
    content = "\t\r\t\a\n"
    test_write(test_str, content)


def run_tests():
    print("EXPECT THE APRS TESTS TO TAKE SOME TIME TO RUN\n")

    test_with_header()
    test_with_no_header()
    test_short_str()
    test_empty_str()
    test_spaces()
    test_escape_chars()

    test_long_str()
