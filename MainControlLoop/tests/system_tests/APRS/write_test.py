from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry
from MainControlLoop.lib.drivers.APRS import APRS




class APRSWriteTest:
    def test_write(self):
        """
        Test APRS write task
        :return: None
        """
        aprs = APRS()
        aprs.functional()
        state_field_registry = StateFieldRegistry()
        aprs_write_task = APRSWriteTask(aprs, state_field_registry)
        message = ""
        while message != "-1":
            message = input("Input what to write (-1 to stop): ")

