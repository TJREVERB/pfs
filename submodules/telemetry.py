import threading


def telemetry_collection():
    while True:
        # Collect subpackets, aggregate, and prioritize
        pass


def gps_subpacket():
    pass


def system_subpacket():
    pass


def on_startup():
    t = threading.Thread(target=telemetry_collection, daemon=True)
    t.start()


def enter_emergency_mode():
    pass


def enter_low_power_mode():
    pass
