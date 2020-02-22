from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry, StateField
from MainControlLoop.lib.drivers.APRS import APRS

from MainControlLoop.tasks.APRS.actuate import APRSBeaconActuateTask
from MainControlLoop.tasks.APRS.actuate import APRSCriticalMessageActuateTask, APRSCriticalMessage
from MainControlLoop.tasks.APRS.actuate import APRSDumpActuateTask
from MainControlLoop.tasks.APRS.actuate import APRSResetActuateTask
from MainControlLoop.tasks.APRS.actuate import APRSResponseActuateTask

from MainControlLoop.tasks.DownLinkProducer import DownLinkProducer


class APRSActuateTest:

    def test_beacon(self):
        aprs = APRS()
        sfr = StateFieldRegistry()
        beacon = APRSBeaconActuateTask(aprs, sfr)

        while True:
            print(f"Expected: `{DownLinkProducer.create_beacon(sfr)}`")
            beacon.run = True
            beacon.execute()
            sf = input("Type in a SF to change OR click enter")
            if sf != '':
                value = input('Value? ')
                t = input('StateField type: ')
                if t == 'int':
                    value = int(sf)
                if t == 'float':
                    value = float(sf)
                try:
                    sf = StateField(sf)
                    sfr.update(sf, value)
                except:
                    print("The StateField you provided is incorrect ")


    def test_dump(self):
        aprs = APRS()
        sfr = StateFieldRegistry()
        dump = APRSDumpActuateTask(aprs, sfr)

        while True:
            print(f"Expected: `{DownLinkProducer.create_dump(sfr)}`")
            dump.run = True
            dump.execute()
            sf = input("Type in a SF to change OR click enter")
            if sf != '':
                value = input('Value? ')
                t = input('StateField type: ')
                if t == 'int':
                    value = int(sf)
                if t == 'float':
                    value = float(sf)
                try:
                    sf = StateField(sf)
                    sfr.update(sf, value)
                except:
                    print("The StateField you provided is incorrect ")
