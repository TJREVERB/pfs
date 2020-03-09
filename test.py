#!/usr/bin/env python
from MainControlLoop.tests.system_tests.APRS import APRSDriverTest, APRSReadTest, APRSActuateTest
from MainControlLoop.tests.system_tests.Iridium import IridiumDriverTest

import inspect
import re

MODULES = {}

# List of tuples: (name, class).
hardware_modules_list = [
    ("APRS Driver", APRSDriverTest),
    ("APRS Read Task", APRSReadTest),
    ("APRS Actuate Tasks", APRSActuateTest)
]
software_modules_list = []


# Test script runs all methods in class.

def run(test_list):
    for name, module_class in test_list:
        confirmation = input(f"Run tests for the {name}? y/[n] ")
        if re.search(r"^(?!n$)y.*$", confirmation, re.IGNORECASE) is not None:
            f = module_class()
            attrs = (getattr(f, name) for name in dir(f))
            methods = filter(inspect.ismethod, attrs)
            for method in methods:
                confirmation = input(f"Run method '{method.__name__}'? y/[n]: ")
                if re.search(r"^(?!n$)y.*$", confirmation, re.IGNORECASE) is not None:
                    try:
                        print(f"Running method '{method.__name__}'")
                        method()
                    except TypeError:
                        pass
                print("-------------------\n")
        print("--------------------------\n")


def test():
    test_type = input("Run system tests or unit tests? ")
    if re.search(r'sys', test_type, re.IGNORECASE) is not None:
        print("Running System Tests")
        print("--------------------------\n")
        run(hardware_modules_list)
    else:
        print("Running Unit Tests")
        print("--------------------------\n")
        run(software_modules_list)


if __name__ == "__main__":
    test()
