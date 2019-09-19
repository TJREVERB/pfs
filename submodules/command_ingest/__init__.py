import logging
from inspect import signature

logger = logging.getLogger("CI")

total_received: int = 0
total_errors: int = 0
total_success: int = 0


# Annotation to register a function as a command
# Example usage:
# @command("aprs_set_bperiod", int)
# def set_bperiod(period: int) -> str:
# ...
def associate(cmd: str):
    """
    Given a function name, return a decorator that registers that function.
    :return: Decorator that registers function.
    """

    valid_commands = {}

    if cmd in valid_commands:
        return valid_commands.get(cmd)
    else:
        return None


def generate_checksum(cmd: str):
    """
    Given a message body, generate its checksum
    :param body: The body of the message.
    :return: Generated checksum for the message.
    """
    cmd_sum = sum([ord(x) for x in cmd])
    cmd_sum %= 26
    cmd_sum += 65
    logger.debug('CHECKOUT :' + chr(cmd_sum) + ";")
    return chr(cmd_sum)


def dispatch(body: str):
    # Get the individual parts of the message
    parts = [part for part in body.split(";") if part]
    command, arguments, checksum = parts[0], parts[1].split(","), parts[2]

    if generate_checksum(command) == checksum:
        associated = associate(command)
        if associated is not None:
            associated_sig = signature(associated)
            # Check num args and arg types

            if not len(arguments) == len(associated_sig.parameters):
                # TODO: log error (incorrect num of args)
                pass
            try:
                associated(*arguments)  # Actually run the command
            except:
                # TODO: send error immediately
                pass
    else:
        # TODO: log that checksum is incorrect
        pass


"""
def start():
    global modules, m_aprs, m_gps, m_adcs, m_eps
    # modules = {'A':core,'B':m_aprs,'C':'iridium','D':'housekeeping','E':'log','F':'GPS'}
    m_aprs = {'a': aprs.enqueue, 'b': aprs.enter_normal_mode, 'c': aprs.enter_low_power_mode,
              'd': aprs.enter_emergency_mode}
    m_gps = {'a': gps.sendgpsthruaprs, 'b': gps.queryfield, 'c': gps.querygps, 'd': gps.querypastgps,
             'e': gps.getsinglegps, 'f': gps.enter_normal_mode, 'g': gps.enter_low_power_mode,
             'h': gps.enter_emergency_mode}
    # m_adcs = {'a': adcs.enter_normal_mode, 'b': adcs.enter_low_power_mode, 'c': adcs.enter_emergency_mode}
    # m_eps = {'a': eps.pin_on, 'b': eps.pin_off, 'c': eps.get_pdm_status, 'd': eps.get_board_status, 'e': eps.set_system_watchdog_timeout, 'f': eps.get_bcr1_volts, 'g': eps.get_bcr1_amps_a, 'h': eps.get_bcr1_amps_b, 'i': eps.get_board_telem, 'j': eps.enter_normal_mode, 'k': eps.enter_low_power_mode, 'l': eps.enter_emergency_mode}
    # m_imu = {'a': imu.enter_normal_mode, 'b': imu.enter_low_power_mode, 'c': imu.enter_emergency_mode}
    # m_iridium = {}  # BLANK - nothing useful is in iridium.py
    # m_housekeeping = {'a': housekeeping.enter_normal_mode, 'b': housekeeping.enter_low_power_mode, 'c': housekeeping.enter_emergency_mode}
    # m_telemetry = {'a': telemetry.gps_subpacket, 'b': telemetry.adcs_subpacket, 'c': telemetry.comms_subpacket, 'd': telemetry.system_subpacket}
    modules = {'B': m_aprs, 'F': m_gps}
    # modules = {'B': m_aprs, 'C': m_iridium, 'D': m_housekeeping, 'F': m_gps, 'G': m_eps, 'H': m_adcs, 'I': m_imu, 'J': m_telemetry}
    # core = {}
"""
