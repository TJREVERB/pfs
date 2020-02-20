#!/usr/bin/env python
from MainControlLoop.tests.system_tests.APRS import APRSDriverTest, APRSReadTest
from MainControlLoop.tests.system_tests.Iridium import IridiumDriverTest

import inspect

MODULES = {}

# List of tuples: (name, class).
hardware_modules_list = [("APRS-Driver", APRSDriverTest), ("APRS-ReadTask", APRSReadTest), ("Iridium", IridiumDriverTest)]
software_modules_list = []

# Test script runs all methods in class.

if __name__ == '__main__':
    for name_type, type_list in [("hardware", hardware_modules_list), ("software", software_modules_list)]:
        for name, moduleClass in type_list:
            if input(f"Run {name_type} tests for test {name}? (Y/N): ").lower() == "y":
                f = moduleClass()
                attrs = (getattr(f, name) for name in dir(f))
                methods = filter(inspect.ismethod, attrs)
                for method in methods:

                    if input(f"Run method '{method.__name__}' in {name_type} test for {name}? (Y/N): ").lower() == "y":
                        try:
                            print(f"Running method '{method.__name__}'")
                            method()
                        except TypeError:
                            pass
