import logging
import time

from . import aprs
from . import gps

logger = logging.getLogger("CI")


def parse_aprs_packet(packet):
    raw_packet = str(packet)
    logger.info("From APRS: " + raw_packet)
    header = raw_packet.find(':')
    if header == -1:
        logger.info("Incomplete header")
        return
    header = raw_packet[:header]
    logger.info("header: " + header)
    data = raw_packet[header + 1:]

    if len(data) == 0:
        logger.debug("Empty body")
        return

    logger.debug("Body: " + data)
    decode(data)


def checksum(body):
    global sum1
    logger.debug(body[0:-7])
    sum1 = sum([ord(x) for x in body[0:-7]])
    sum1 %= 128
    logger.debug('CHECKOUT :' + chr(sum1) + ";")
    return chr(sum1) == body[-7]


def decode(body):
    logger.debug(body[-5:-1])
    logger.debug(body[0:2])
    if body[0:2] == 'TJ' and body[-5:-1] == '\\r\\n' and checksum(body):
        logger.debug('Valid message')
        logger.debug(body[4:-7])
        try:
            modules[body[2]][body[3]](body[4:-7])
        except KeyError:
            # Invalid command format was send
            logger.warning("Invalid command with correct checksum")
    elif body[0:2] == 'T#':  # Telemetry Packet: APRS special case
        aprs.last_telem_time = time.time()
        aprs.beacon_seen = True
        aprs.pause_sending = True
        logger.debug('Telem heartbeat received')
    else:
        logger.debug('Invalid message')


def piprint(packet):
    print("FROM APRS: " + str(packet))


def on_startup():
    global modules, m_aprs, m_gps
    # modules = {'A':core,'B':m_aprs,'C':'iridium','D':'housekeeping','E':'log','F':'GPS'}
    m_aprs = {'a': aprs.send, 'b': aprs.dump}
    m_gps = {'a': gps.sendgpsthruaprs}
    modules = {'B': m_aprs, 'F': m_gps}
    # core = {}
