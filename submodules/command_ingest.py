import logging
import time
from . import aprs
from . import gps

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
    global modules, m_aprs, m_gps
    # modules = {'A':core,'B':m_aprs,'C':'iridium','D':'housekeeping','E':'log','F':'GPS'}
    m_aprs = {'a': aprs.enqueue}
    m_gps = {'a': gps.sendgpsthruaprs}
    modules = {'B': m_aprs, 'F': m_gps}
    # core = {}
