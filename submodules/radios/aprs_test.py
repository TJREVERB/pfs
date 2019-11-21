from pty import openpty
from os import ttyname, read, write

from submodules.radios.aprs import APRS

config = {
    "aprs": {
        "serial_port": ""
    }
}

WORDS = ["Wood", "Low hanging FrUit", "documentation"]
PORT = "FAKE"


class FakeTelemetry:
    def __init__(self, expected_data, always_print=False):
        self.expected_data = expected_data
        self.always_print = always_print

    def enqueue(self, message):
        _assert = self.expected_data == message
        if not _assert or self.always_print:
            print(
                f"received: {list(message)}, expected: {list(self.expected_data)}")
        assert _assert


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


def test_write(test_str, content):
    aprs, master = start_fake(content)
    aprs.start()

    for c in test_str:
        b = c.encode("utf-8")
        write(master, b)


def test_read(word):
    aprs, master = start_fake("na")
    aprs.start()

    aprs.send(f"{word}")

    result = ""
    expected = f"{word}\n"

    last_item = ""
    while not last_item == "\n":
        last_item = read(master, 1).decode('utf-8')
        result += last_item

    _assert = result == expected
    if not _assert:
        print(
            f"received: {list(result)}, expected: {list(expected)}")
        assert _assert


def test_g2f_with_header():
    for word in WORDS:
        test_str = f"header:{word}\n"
        content = f"{word}\n"
        test_write(test_str, content)


def test_g2f_with_no_header():
    print(f"Expect {len(WORDS)} `Incomplete APRS header!`")
    for word in WORDS:
        test_str = f"{word}\n"
        content = f"{word}\n"
        test_write(test_str, content)


def test_f2g_normal():
    for word in WORDS:
        test_read(word)


def test_g2f_long_str():
    test_str = f"header:{'182nzfei92' * 5000}\n"
    content = '182nzfei92' * 5000 + "\n"
    test_write(test_str, content)


def test_f2g_long_str():
    test_read('182nzfei92' * 100)


def test_g2f_short_str():
    test_str = f"header:i\n"
    content = "i\n"
    test_write(test_str, content)


def test_f2g_short_str():
    test_read("a")


def test_g2f_empty_str():
    test_str = "header:\n"
    content = "\n"
    test_write(test_str, content)


def test_f2g_empty_str():
    test_read("")


def test_g2f_spaces():
    test_str = "header:        \n"
    content = "        \n"
    test_write(test_str, content)


def test_f2g_spaces():
    test_read("                      ")


def test_g2f_escape_chars():
    test_str = "header:\t\r\t\a\n"
    content = "\t\r\t\a\n"
    test_write(test_str, content)


def test_f2g_escape_chars():
    test_read("\t\r\t\a")


def ground_to_pfs(port="FAKE", fast=False):
    print("EXPECT THE APRS TESTS TO TAKE SOME TIME TO RUN\n\n")

    print("GROUND STATION -> pFS Test Running... \n")
    if port == "FAKE":
        tests = [
            test_g2f_with_header,
            test_g2f_with_no_header,
            test_g2f_short_str,
            test_g2f_empty_str,
            test_g2f_spaces,
            test_g2f_escape_chars
        ]
        for count, test in enumerate(tests):
            print(f"RUNNING TEST {count}.....\n")
            test()
        if not fast:
            print(f"RUNNING TEST {count + 1}")
            # takes a while to run long str
            test_g2f_long_str()
    else:
        config["aprs"]["serial_port"] = port
        while True:
            expected_data = input("What message should pFS receive? ") + "\n"
            modules = {
                "telemetry": FakeTelemetry(expected_data, always_print=True)
            }
            aprs = APRS(config)
            aprs.set_modules(modules)
            aprs.start()


def pfs_to_ground(port="FAKE", fast=False):
    print("EXPECT THE APRS TESTS TO TAKE SOME TIME TO RUN\n\n")

    print("pFS -> GROUND STATION Test Running....\n")
    if port == "FAKE":
        tests = [test_f2g_normal, test_f2g_short_str, test_f2g_empty_str, test_f2g_spaces, test_f2g_escape_chars]
        for count, test in enumerate(tests):
            print(f"RUNNING TEST {count}.....\n")
            test()

        if not fast:
            print(f"RUNNING TEST {count + 1}.....\n")
            # takes a while to run long str
            test_f2g_long_str()
    else:
        config["aprs"]["serial_port"] = port
        while True:
            message = input("What message should pFS send? ")
            modules = {
                "telemetry": FakeTelemetry(message, always_print=True)
            }
            aprs = APRS(config)
            aprs.set_modules(modules)
            aprs.start()
            aprs.send(message)


def run_tests(port="FAKE"):
    ground_to_pfs(port)
    pfs_to_ground(port)
