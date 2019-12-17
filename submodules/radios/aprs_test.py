from pty import openpty
from os import ttyname, read, write, system

from submodules.radios.aprs import APRS

config = {"aprs": {"serial_port": ""}}

WORDS = ["Wood", "Low hanging FrUit", "documentation"]
PORT = "FAKE"


class FakeTelemetry:
    def __init__(self, expected_data, always_print=False, try_assert=True):
        self.expected_data = expected_data
        self.always_print = always_print
        self.try_assert = try_assert

    def enqueue(self, message):
        _assert = self.expected_data == message
        if not _assert or self.always_print:
            print()
            print()
            print(f"received: {list(message)}, expected: {list(self.expected_data)}")
            print()
            print()
        if self.try_assert:
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

    modules = {"telemetry": FakeTelemetry(expected_data)}
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
        last_item = read(master, 1).decode("utf-8")
        result += last_item

    _assert = result == expected
    if not _assert:
        print(f"received: {list(result)}, expected: {list(expected)}")
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
    content = "182nzfei92" * 5000 + "\n"
    test_write(test_str, content)


def test_f2g_long_str():
    test_read("182nzfei92" * 100)


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


def simulate_ground_to_pfs(fast=False):
    print("EXPECT THE APRS TESTS TO TAKE SOME TIME TO RUN\n\n")

    print("GROUND STATION -> pFS Test Running... \n")
    tests = [
        test_g2f_with_header,
        test_g2f_with_no_header,
        test_g2f_short_str,
        test_g2f_empty_str,
        test_g2f_spaces,
        test_g2f_escape_chars,
    ]
    for count, test in enumerate(tests):
        print(f"RUNNING TEST {count}.....\n")
        test()
    if not fast:
        print(f"RUNNING TEST {count + 1}")
        # takes a while to run long str
        test_g2f_long_str()


def simulate_pfs_to_ground(fast=False):
    print("EXPECT THE APRS TESTS TO TAKE SOME TIME TO RUN\n\n")

    print("pFS -> GROUND STATION Test Running....\n")
    tests = [
        test_f2g_normal,
        test_f2g_short_str,
        test_f2g_empty_str,
        test_f2g_spaces,
        test_f2g_escape_chars,
    ]
    for count, test in enumerate(tests):
        print(f"RUNNING TEST {count}.....\n")
        test()

    if not fast:
        print(f"RUNNING TEST {count + 1}.....\n")
        # takes a while to run long str
        test_f2g_long_str()


def aprs_hardware_testing(port):
    def clear():
        system('clear')
    config["aprs"]["serial_port"] = port
    telem = FakeTelemetry("", always_print=True, try_assert=False)
    modules = {"telemetry": telem}
    aprs = APRS(config)
    aprs.set_modules(modules)
    aprs.start()

    clear()
    print("Interactive APRS Testing shell")
    print("Anything pFS receives will be printed to the console.")
    print("Type in help to see the commands")

    while True:
        cmd = input("")
        args = cmd.split(" ")
        if cmd == "help":
            print()
            print("Type in `help` to get help")
            print("Type in `send {MESSAGE}` to send a message")
            print("Type in `send-l {X}` to send a str of length X")
            print("Type in `send-o {X} {Y}` to send a str of length X, Y Times")
            print("Type in `send-c {X} {C}` to send a str with length X filled with the substring C")
            print("Type in `clear` to clear the console")
            print("Type `exit` to quit")
            print()

        elif args[0] == "send":
            aprs.send(" ".join(args[1:]))
        elif args[0] == "send-l":
            aprs.send(int(args[1]) * 'A')
        elif args[0] == "send-o":
            for i in range(int(args[2])):
                aprs.send(int(args[1]) * 'A')
        elif args[0] == "send-c":
            aprs.send(int(args[1]) * " ".join(args[2:]))
        elif args[0] == "exit":
            return
        elif args[0] == "clear":
            clear()
        elif cmd == "":
            continue
        else:
            print(f"Command `{cmd}` not found.")


def run_tests():
    simulate = input("Are you testing hardware + software? [y]/N ") == 'N'
    if simulate:
        fast = not input("Test slow methods? [y]/N ") == 'N'
        simulate_ground_to_pfs(fast)
        simulate_pfs_to_ground(fast)
        return

    port = input("What port is APRS on? (default /dev/ttyACM0) ")
    if not port:
        port = '/dev/ttyAMC0'
    aprs_hardware_testing(port)

