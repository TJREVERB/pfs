from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry, StateField
from MainControlLoop.lib.drivers.APRS import APRS

from MainControlLoop.tasks.APRS.actuate import APRSBeaconActuateTask
from MainControlLoop.tasks.APRS.actuate import APRSCriticalMessageActuateTask, APRSCriticalMessage
from MainControlLoop.tasks.APRS.actuate import APRSDumpActuateTask
from MainControlLoop.tasks.APRS.actuate import APRSResetActuateTask
from MainControlLoop.tasks.APRS.actuate import APRSResponseActuateTask

from MainControlLoop.tasks.DownLinkProducer import DownLinkProducer


class APRSActuateTest:

    def update_an_sfr(self, sfr):
        state_field = input("Type in a SF to change OR click enter ")
        if state_field != '':
            try:
                state_field = StateField(state_field)
            except:
                print("The StateField you provided is incorrect ")
                return

            value = input('Value? ')
            value_type = input('StateField type: ')
            if value_type == 'int':
                value = int(value)
            if value_type == 'float':
                value = float(value)
            if value_type == 'bool':
                value = value == 'True'
            sfr.update(state_field, value)

    def test_beacon(self):
        aprs = APRS()
        sfr = StateFieldRegistry()
        beacon = APRSBeaconActuateTask(aprs, sfr)

        while True:
            self.update_an_sfr(sfr)
            print(f"Expected: `{DownLinkProducer.create_beacon(sfr)}`")
            beacon.set_beacon(DownLinkProducer.create_beacon(sfr))
            beacon.run = True
            beacon.execute()

    def test_dump(self):
        aprs = APRS()
        sfr = StateFieldRegistry()
        dump = APRSDumpActuateTask(aprs, sfr)

        while True:
            self.update_an_sfr(sfr)
            print(f"Expected: `{DownLinkProducer.create_dump(sfr)}`")
            dump.set_dump(DownLinkProducer.create_dump(sfr))
            dump.run = True
            dump.execute()

    def test_response(self):
        aprs = APRS()
        sfr = StateFieldRegistry()
        response = APRSResponseActuateTask(aprs, sfr)
        while True:
            self.update_an_sfr(sfr)
            try:
                state_field = StateField(input("What StateField should be sent in the response? "))
            except:
                print("The StateField you provided is incorrect")
                continue
            print(f"Expected: `{DownLinkProducer.create_response(sfr, state_field)}`")
            response.set_response(DownLinkProducer.create_response(sfr, state_field))
            response.run = True
            response.execute()

    def test_critical(self):
        aprs = APRS()
        sfr = StateFieldRegistry()
        critical = APRSCriticalMessageActuateTask(aprs, sfr)
        while True:
            try:
                message = APRSCriticalMessage(input("Critical message type? "))
            except:
                print("Incorrect message type")
                continue
            critical.set_message(message)
            critical.run = True
            critical.execute()

    def test_reset(self):
        aprs = APRS()
        sfr = StateFieldRegistry()
        reset = APRSResetActuateTask(aprs, sfr)
        reset.run = True
        reset.execute()
