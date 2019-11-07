import os
import unittest
from os import ttyname

from os import ttyname, read, write
from threading import Thread
from pty import openpty
import serial

from submodules import aprs, telemetry
from core.error import Error
from core.log import Log
from datetime import datetime
import yaml

master, slave = openpty()
port_name = ttyname(slave)


class TestCase1(unittest.TestCase):
    """
    Simulate a send from flight to the ground station
    Normal-sized string that fits within bounds
    NOTE: Timestamp is fixed (1570742093) for ease of testing purposes
    """

    def test_something(self):
        telemetry.enqueue(Error('TEST', datetime.fromtimestamp(1570742093), "H3ll0th3r3t#is!sanError"))
        output = read(master, 55)
        self.assert_(output == 'RVJSITpURVNUOjIwMTkvMTAvMTBAMTcuMTQuNTM6SDNsbDB0aDNyM3QjaXMhc2FuRXJyb3I=')


class TestCase2(unittest.TestCase):
    """
    Simulate a send from flight to the ground station
    Long string
    """

    def test_something(self):
        telemetry.enqueue(Error('TEST', datetime.fromtimestamp(1570742093),
                                "H3ll0th3r3t#is!sanErrorThatIsVeryLongAndIsGreaterThan170BytesAndICan'tThinkOfAnyOtherWayToMakeThis170BytesSoIAmMakingItQuiteLong.IHateAP-PhysicsAndIAmNotDoingSo Well in AP Physics right now."))
        output = read(master, 55)
        self.assertEquals(
            output, "RVJSITpURVNUOjIwMTkvMTAvMTBAMTcuMTQuNTM6SDNsbDB0aDNyM3QjaXMhc2FuRXJyb3JUaGF0SXNWZXJ5TG9uZ0FuZElzR3JlYXRlclRoYW4xNzBCeXRlc0FuZElDYW4ndFRoaW5rT2ZBbnlPdGhlcldheVRvTWFrZVRoaXMxNzBCeXRlc1NvSUFtTWFraW5nSXRRdWl0ZUxvbmcuSUhhdGVBUC1QaHlzaWNzQW5kSUFtTm90RG9pbmdTbyBXZWxsIGluIEFQIFBoeXNpY3MgcmlnaHQgbm93Lg==")


class TestCase3(unittest.TestCase):
    """
    Simulate a send from flight to the ground station
    Short string
    """

    def test_something(self):
        telemetry.enqueue(Log('TEST2', "INFO", datetime.fromtimestamp(1570742093), "H"))
        output = read(master, 35)
        self.assert_(output == "TE9HJjpURVNUMjpJTkZPOjIwMTkvMTAvMTBAMTcxNDUzOkg=")


class TestCase4(unittest.TestCase):
    """
    Simulate a send from flight to the ground station
    Empty string
    """

    def test_something(self):
        telemetry.enqueue(Log('TEST2', "INFO", datetime.fromtimestamp(1570742093), ""))
        output = read(master, 34)
        self.assert_(output == 'TE9HJjpURVNUMjpJTkZPOjIwMTkvMTAvMTBAMTcxNDUzOg==')


class TestCase5(unittest.TestCase):
    """
    Simulate a send from flight to the ground station
    String of spaces
    """

    def test_something(self):
        telemetry.enqueue(Log('TEST2', "INFO", datetime.fromtimestamp(1570742093), "       "))
        output = read(master, 34)
        self.assert_(output == 'TE9HJjpURVNUMjpJTkZPOjIwMTkvMTAvMTBAMTcxNDUzOiAgICAgICA=')


class TestCase6(unittest.TestCase):
    """
    Simulate a send from flight to the ground station
    String of newlines and escape characters
    """

    def test_something(self):
        telemetry.enqueue(Error('TEST2', datetime.fromtimestamp(1570742093), "\n\n\n\\\\\\\t\r"))
        output = read(master, 34)
        self.assert_(output == 'RVJSITpURVNUMjoyMDE5LzEwLzEwQDE3LjE0LjUzOlxuXG5cblxcXFxcXFx0XHI=')


class TestCase7(unittest.TestCase):
    """
    Simulate a send from GS to flight
    Normal-sized string that fits within bounds
    """

    def test_something(self):
        telemetry.enqueue(Error('TEST2', datetime.fromtimestamp(1570742093), ""))
        output = read(master, 34)
        self.assert_(output == 'RVJSITpURVNUMjoyMDE5LzEwLzEwQDE3LjE0LjUzOlxuXG5cblxcXFxcXFx0XHI=')

def load_config():
    """
    Loads a YAML file to be used as the `config`.
    If `config_custom.yml` exists, use that (this is user-configurable).
    Else, use `config_default.yml`. This should not be changed while testing.
    """
    config = None
    # `config_custom.yml` (custom configuration file) exists
    if os.path.exists('../config/config_custom.yml'):
        # TODO: be resilient to I/O errors (e.g. persistent storage is ded)
        with open('../config/config_custom.yml') as f:
            config = yaml.load(f)
    else:
        # Custom configuration does not exist, use `config_default.yml`
        with open('../config/config_default.yml') as f:
            config = yaml.load(f)

    return config

if __name__ == '__main__':
    print(port_name)
    telemetry.config = load_config()
    unittest.main()
