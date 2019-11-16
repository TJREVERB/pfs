MODULES = {}
# Try to import test cases, ignore modules on fail
try:
    from submodules.antenna_deploy.tests import run_tests as run_antenna_tests
    MODULES["antenna"] = run_antenna_tests
except:
    MODULES["antenna"] = False
try:
    from submodules.command_ingest.tests import run_tests as run_command_tests
    MODULES["command"] = run_command_tests
except:
    MODULES["command"] = False
try:
    from submodules.eps.tests import run_tests as run_eps_tests
    MODULES["eps"] = run_eps_tests
except:
    MODULES["eps"] = False
try:
    from submodules.radios.aprs_test import run_tests as run_aprs_tests
    MODULES["radio.aprs"] = run_aprs_tests
    APRS_PORT = "FAKE"
except:
    MODULES["radios.aprs"] = False
try:
    from submodules.radios.iridium_tests import run_tests as run_iridium_tests
    MODULES["radios.iridium"] = run_iridium_tests
except:
    MODULES["radios.iridium"] = False
try:
    from submodules.telemetry.tests import run_tests as run_telemetry_tests
    MODULES["telemetry"] = run_telemetry_tests
except:
    MODULES["telemetry"] = False

if __name__ == '__main__':
    for module, func in MODULES.items():
        if func:
            print(f"Running test cases for module {module}")
            func()
        else:
            print(f"run_tests not found for module {module}")
