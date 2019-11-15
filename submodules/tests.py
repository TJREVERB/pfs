MODULES = {
    "antenna": True,
    "command": True,
    "eps": True,
    "radios.aprs": True,
    "radios.iridium": True,
    "telemetry": True
}

# Try to import test cases, ignore modules on fail
try:
    from submodules.antenna_deploy.tests import run_tests as run_antenna_tests
except:
    MODULES["antenna"] = False
try:
    from submodules.command_ingest.tests import run_tests as run_command_tests
except:
    MODULES["command"] = False
try:
    from submodules.eps.tests import run_tests as run_eps_tests
except:
    MODULES["eps"] = False
try:
    from submodules.radios.aprs_test import run_tests as run_aprs_tests
    APRS_PORT = "FAKE"
except:
    MODULES["radios.aprs"] = False
try:
    from submodules.radios.iridium_tests import run_tests as run_iridium_tests
except:
    MODULES["radios.iridium"] = False
try:
    from submodules.telemetry.tests import run_tests as run_telemetry_tests
except:
    MODULES["telemetry"] = False

if __name__ == '__main__':
    if MODULES["antenna"]:
        run_antenna_tests()
    if MODULES["command"]:
        run_command_tests()
    if MODULES["eps"]:
        run_eps_tests()
    if MODULES["radios.aprs"]:
        run_aprs_tests(APRS_PORT)
    if MODULES["radios.iridium"]:
        run_iridium_tests()
    if MODULES["telemetry"]:
        run_telemetry_tests()
