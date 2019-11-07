import unittest
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
        print(message)
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


class CubeSatToGroundStation(unittest.TestCase):
    def test_normal_str(self):
        self.assertEqual(True, False)

    def test_long_str(self):
        self.assertEqual(True, False)

    def test_short_str(self):
        self.assertEqual(True, False)

    def test_empty_str(self):
        self.assertEqual(True, False)

    def test_spaces(self):
        self.assertEqual(True, False)

    def test_escape_chars(self):
        self.assertEqual(True, False)

    def close_port(self):
        self.assertEqual(True, False)


class GroundStationToCubeSat(unittest.TestCase):
    def test_normal_str(self):
        test_str = "no: header\n"
        aprs, master = start_fake(test_str)
        aprs.start()
        for c in test_str:
            b = c.encode("utf-8")
            write(master, b)

        self.assertEqual(True, True)

    def test_long_str(self):
        self.assertEqual(True, False)

    def test_short_str(self):
        self.assertEqual(True, False)

    def test_empty_str(self):
        self.assertEqual(True, False)

    def test_spaces(self):
        self.assertEqual(True, False)

    def test_escape_chars(self):
        self.assertEqual(True, False)

    def close_port(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
