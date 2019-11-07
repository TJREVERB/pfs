"""
README BEFORE USING
Telemetry's __init__.py must be changed in several places before using this.

* The reference to the config file in dump()'s while loop must be changed to a number, not referencing config.
* radio_output.send() in the dump() method must be changed with a print statement.
    Alternatively, radio_output.send() can be changed similarly.
* Command_ingest.enqueue() should be commented out or replaced with a dummy thing.
* The two lines at the end of start() that start the decide() thread should be commented out, and the while-True
    loop in decide() must be commented out. Indents need to be fixed accordingly.
    This script runs decide() as a one-off method

"""

"""
A script to test telemetry. Changes must be made as above before using.
When "ready" is printed, type any one of:

* ee - enqueue an error
* el - enqueue a log
* eXXX where XXX is any text that begins with a semicolon - run telemetry.enqueue(XXX)
* d - run a dump
* p - print the general queue, error stack, and log stack in that order
* c - clear buffers

"""

from datetime import datetime
from submodules import telemetry
from core import error, log
from yaml import load
from os import ttyname, openpty
from submodules import radios
from submodules.radios import aprs, iridium
from submodules.radios.aprs import *
from submodules.radios.iridium import *

def main():
    master, slave = openpty()
    port_name = ttyname(slave)
    print(port_name)

    config = load(open("../../config/config_default.yml"))
    config['aprs']['serial_port'] = port_name
    print(config)
    telemObj = telemetry.Telemetry(config)
    aprsObj = APRS(config)
    iridumObj = Iridium(config)

    modules = {"aprs": aprsObj,
            "command_ingest": None,
            "eps": None,
            "iridium": iridumObj,
            "telemetry": telemObj,
        }

    telemObj.set_modules(modules)
    iridumObj.set_modules(modules)
    aprsObj.set_modules(modules)

    telemObj.start()
    iridumObj.start()
    aprsObj.start()

    while True:
        print("Ready")
        c = input()
        if c[0] == 'e':
            if c[1] == 'e':
                telemObj.enqueue(error.Error("TEST", datetime.utcnow(), "testing"))
            elif c[1] == 'l':
                telemObj.enqueue(log.Log("TEST", "INFO", datetime.utcnow(), "testinglog"))
            else:
                telemObj.enqueue(c[1:])
        elif c[0] == 'd':
            telemObj.dump()
        elif c[0] == 'p':
            print(telemObj.general_queue, telemObj.err_stack, telemObj.log_stack)
        elif c[0] == 'c':
            telemObj.clear_buffers()


if __name__ == '__main__':
    main()
