from MainControlLoop.lib.drivers.APRS import APRS

from time import sleep


class APRSDriverTest:

    def test_read(self):
        """
        Test APRS read driver.
        When the message "0" is received, break.
        :return: None
        """
        aprs = APRS()
        while True:
            message = aprs.read()
            print("Got message:", message)
            if message == "0":
                break

            sleep(1)

    def test_write(self):
        """
        Test case for the APRS Write driver.
        Takes input from stdin.
        When the message "-1" is received, break.
        :return: None
        """
        aprs = APRS()
        while True:
            message = input("Input message to write (-1 to stop): ")
            if message == "-1":
                break

            aprs.write(message)

    def test_functional(self):
        aprs = APRS()
        while True:
            stop = ''
            stop += input("Disable the APRS, and click enter ")
            print(f"APRS function == {aprs.functional()}")
            stop += input("Enable the APRS, and click enter ")
            print(f"APRS function == {aprs.functional()}")
            if '-1' in stop:
                break
