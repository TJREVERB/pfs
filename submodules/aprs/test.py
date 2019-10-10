import unittest
from os import ttyname

from os import ttyname, read, write
from threading import Thread
from pty import openpty
import serial

master, slave = openpty()
port_name = ttyname(slave)

class TestCase1(unittest.TestCase):
    """
    hello
    """
    def test_something(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
