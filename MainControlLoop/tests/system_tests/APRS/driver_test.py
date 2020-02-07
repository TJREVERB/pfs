from MainControlLoop.lib.drivers.APRS import APRS

from time import sleep


class APRSDriverTest:

    def test_read(self):
        """
        Test APRS read task.
        When the message "0" is received, break.
        :return: None
        """
        aprs = APRS()
        aprs.functional()
        while True:
            message = aprs.read()
            print("Got message:", message)
            if message == "0":
                break

            sleep(1)

    def test_write(self):
        """
        Test case for the APRS Write task.
        Takes input from stdin.
        When the message "0" is received, break.
        :return: None
        """
        aprs = APRS()
        aprs.functional()
        while True:
            message = input("Input message to write: ")
            if message == "0":
                break
            aprs.write(message)
