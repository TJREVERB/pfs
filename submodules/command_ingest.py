import logging

from . import aprs
from . import gps

logger = logging.getLogger("CI")


def dispatch_command(packet):
    logger.debug("dispatch called")
    rawpacket = str(packet)
    logger.info("From APRS: " + RAWPACKET)
    headerfindresult = rawpacket.find(':')
    if headerfindresult == -1:
        logger.info("Incomplete header")
        return
    header = rawpacket[:headerfindresult]
    logger.info("header: " + HEADER)
    datacontent = rawpacket[headerfindresult + 1:]

    if len(datacontent) == 0:
        logger.info("Empty body")
        return

    logger.info("Body: " + datacontent)
    decode(datacontent)


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
        modules[body[2]][body[3]](body[4:-7])
    elif body[0:2] == 'T#':
        aprs.didigettelem = True
        aprs.pausesend = True
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
