from MainControlLoop.lib.drivers.Iridium import Iridium


class IridiumDriverTest:
    def test_read(self):
        """
        Test Iridium read task.
        When the message "0" is received, break.
        :return: None
        """
        iridium = Iridium()
        iridium.functional()
        while True:
            message = iridium.read()
            print("Got message:", message)
            if message == "0":
                break

    def test_write(self):
        """
        Test case for the Iridium Write task.
        Takes input from stdin.
        When the message "0" is received, break.
        :return: None
        """
        iridium = Iridium()
        iridium.functional()
        while True:
            message = input("Input message to write: ")
            if message == "0":
                break
            iridium.write(message)
