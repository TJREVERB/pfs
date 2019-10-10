"""
README BEFORE USING
Telemetry's __init__.py must be changed in several places before using this.

* The reference to the config file in dump()'s while loop must be changed to a number, not referencing config.
* radio_output.send() in the dump() method must be changed with a print statement.
    Alternatively, radio_output.send() can be changed similarly.
* Command_ingest.enqueue() should be commented out or replaced with a dummy thing.
* The two lines at the end of start() that start the decide() thread should be commented out, and the while-True
    loop in decide() must be commented out (but not the contents of the loop, just the header).
    Indents need to be fixed accordingly. This script runs decide() as a one-off method.

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

def main():
    while True:
        print("Ready")
        c = input()
        if c[0] == 'e':
            if c[1] == 'e':
                telemetry.enqueue(error.Error("TEST", datetime.utcnow(), "testing"))
            elif c[1] == 'l':
                telemetry.enqueue(log.Log("TEST", "INFO", datetime.utcnow(), "testinglog"))
            else:
                telemetry.enqueue(c[1:])
            telemetry.decide()
        elif c[0] == 'd':
            telemetry.dump()
        elif c[0] == 'p':
            print(telemetry.general_queue, telemetry.err_stack, telemetry.log_stack)
        elif c[0] == 'c':
            telemetry.clear_buffers()


if __name__ == '__main__':
    telemetry.start()
    main()
