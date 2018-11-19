import logging
import time
from . import aprs
from . import gps

# from . import adcs
# from . import eps
# from . import imu
# from . import iridium
# from . import telemetry

logger = logging.getLogger("CI")

total_recieved: int = 0
total_errors: int = 0
total_success: int = 0


def generate_checksum(body: str):
    global sum1
    logger.debug(body[0:-7])
    sum1 = sum([ord(x) for x in body[0:-7]])
    sum1 %= 26
    sum1 += 65
    logger.debug('CHECKOUT :' + chr(sum1) + ";")
    return chr(sum1)


def dispatch(body: str):
    global total_errors, total_recieved, total_success
    logger.debug(body[-5:-1])
    logger.debug(body[0:2])
    if body[0:2] == 'TJ' and body[-5:-1] == '\\r\\n' and generate_checksum(body) == body[-7]:
        total_recieved += 1
        logger.debug('Valid message')
        logger.debug(body[4:-7])
        try:
            # execute command
            modules[body[2]][body[3]](body[4:-7])
            aprs.last_message_time = time.time()  # Update the last command time
            total_success += 1
        except:
            # Invalid command format was send
            logger.warning("Invalid command with correct checksum")
            total_errors += 1
    elif body[0:2] == 'T#':  # Telemetry Packet: APRS special case
        aprs.last_telem_time = time.time()
        aprs.beacon_seen = True
        aprs.pause_sending = True
        logger.debug('Telem heartbeat received')
    else:
        logger.debug('Invalid message')


def on_startup():
    global modules, m_aprs, m_gps, m_adcs, m_eps
    # modules = {'A':core,'B':m_aprs,'C':'iridium','D':'housekeeping','E':'log','F':'GPS'}
    m_aprs = {'a': aprs.enqueue, 'b': aprs.enter_normal_mode, 'c': aprs.enter_low_power_mode,
              'd': aprs.enter_emergency_mode}
    m_gps = {'a': gps.sendgpsthruaprs, 'b': gps.queryfield, 'c': gps.querygps, 'd': gps.querypastgps,
             'e': gps.getsinglegps, 'f': gps.enter_normal_mode, 'g': gps.enter_low_power_mode,
             'h': gps.enter_emergency_mode}
    # m_adcs = {'a': adcs.enter_normal_mode, 'b': adcs.enter_low_power_mode, 'c': adcs.enter_emergency_mode}
    # m_eps = {'a': eps.pin_on, 'b': eps.pin_off, 'c': eps.get_PDM_status, 'd': eps.get_board_status, 'e': eps.set_system_watchdog_timeout, 'f': eps.get_BCR1_volts, 'g': eps.get_BCR1_amps_A, 'h': eps.get_BCR1_amps_B, 'i': eps.get_board_telem, 'j': eps.enter_normal_mode, 'k': eps.enter_low_power_mode, 'l': eps.enter_emergency_mode}
    # m_imu = {'a': imu.enter_normal_mode, 'b': imu.enter_low_power_mode, 'c': imu.enter_emergency_mode}
    # m_iridium = {}  # BLANK - nothing useful is in iridium.py
    # m_housekeeping = {'a': housekeeping.enter_normal_mode, 'b': housekeeping.enter_low_power_mode, 'c': housekeeping.enter_emergency_mode}
    # m_telemetry = {'a': telemetry.gps_subpacket, 'b': telemetry.adcs_subpacket, 'c': telemetry.comms_subpacket, 'd': telemetry.system_subpacket}
    modules = {'B': m_aprs, 'F': m_gps}
    # modules = {'B': m_aprs, 'C': m_iridium, 'D': m_housekeeping, 'F': m_gps, 'G': m_eps, 'H': m_adcs, 'I': m_imu, 'J': m_telemetry}
    # core = {}
