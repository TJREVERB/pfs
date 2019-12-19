import inspect
from io import StringIO
from unittest.mock import patch

from submodules.telemetry.test import fakeAPRS, fakeCI
from submodules import telemetry
from yaml import safe_load
from helpers import error, log
from time import sleep


class TelemetryTest():
    def test_Error(self):
        # Load everything
        telem = init()

        telem.enqueue(error.Error("TEST", msg="Hellothisisatest123!"))
        sleep(3)
        output = ""

        with patch('sys.stdout', new=StringIO()) as fake_out:
            telem.dump()
            sleep(2)
            output = fake_out.getvalue()

        print(output)

    def test_Log(self):
        telem = init()

        telem.enqueue(log.Log("TEST", msg="Hellothisisatestofalogand I_- hate AP Phys!cs C"))
        sleep(3)
        output = ""

        with patch('sys.stdout', new=StringIO()) as fake_out:
            telem.dump()
            sleep(2)
            output = fake_out.getvalue()

        print(output)

    def test_CI(self):
        telem = init()

        with patch('sys.stdout', new=StringIO()) as fake_out:
            telem.enqueue("CMD$hello;")
            sleep(3)
            output = fake_out.getvalue()

        print(output)

    def test_Nonsense(self):
        telem = init()

        telem.enqueue("slkfjahskuyabw9eryabsdiufahber87a63bo0a97bO(^VO(#^$V*OA@76vao9")
        sleep(3)
        output = ""

        with patch('sys.stdout', new=StringIO()) as fake_out:
            telem.dump()
            sleep(2)
            output = fake_out.getvalue()

        print(output)

    def test_ReallyLongError(self):
        telem = init()

        telem.enqueue(error.Error("TEST", msg="Hello I hate AP Physics and Multi with Dr. Osborne, I'm going to end the semester with, like, a 70 or something. I wish I went to the SLOB today and got my free 2 points instead of going to Ozzy test corrections :("))
        sleep(3)
        output = ""

        with patch('sys.stdout', new=StringIO()) as fake_out:
            telem.dump()
            sleep(2)
            output = fake_out.getvalue()

        print(output)

    def test_SeriesOfMessages(self):
        telem = init()

        telem.enqueue(error.Error("TEST", msg="Hellothisisatest123!"))
        sleep(0.5)
        telem.enqueue(error.Error("TEST", msg="Hellothisistheseconderror"))
        telem.enqueue(error.Error("TEST", msg="APRS: Attempted to enqueue invalid message"))
        telem.enqueue(log.Log("EPS", msg="Battery voltage: 50%"))
        sleep(0.5)
        telem.enqueue(error.Error("TEST", msg="Hellothisistheseconderror"))
        telem.enqueue(error.Error("TEST", msg="APRS: Attempted to enqueue invalid message"))
        telem.enqueue(log.Log("EPS", msg="Battery voltage: 2%"))
        telem.enqueue(log.Log("CORE", msg="Entering emergency mode"))

        sleep(3)
        output = ""

        with patch('sys.stdout', new=StringIO()) as fake_out:
            telem.dump()
            sleep(10)    # More time for more messages
            output = fake_out.getvalue()

        print(output)



def run_tests():
    """
    Run tests in test/__init__.py
    Prints outputs to screen
    """
    test = TelemetryTest()
    attrs = (getattr(test, name) for name in dir(test))
    methods = filter(inspect.ismethod, attrs)
    for method in methods:
        print("Running test", method.__name__)
        method()


def init() -> telemetry:
    """
    Init a telemetry object
    :return: A telemetry object
    """
    with open('config/config_custom.yml') as f:
        config = safe_load(f)
    submodules = {
        "antenna_deployer": None,
        "aprs": fakeAPRS.fakeAPRS(config),
        "command_ingest": fakeCI.FakeCommandIngest(config),
        "eps": None,
        "iridium": None,
        "telemetry": None,
    }
    telem = telemetry.Telemetry(config)
    telem.set_modules(submodules)

    for submodule in submodules.values():
        if submodule is not None:
            submodule.start()
    telem.start()

    return telem