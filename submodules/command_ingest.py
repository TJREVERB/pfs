import logging

from . import aprs
from . import gps


def dispatch_command(packet):
    logging.debug("DISPATCH CALLED")
    rawpacket = str(packet)
    logging.info("FROM APRS: " + rawpacket)
    headerfindresult = rawpacket.find(':')
    if headerfindresult == -1:
        logging.info("INCOMPLETE HEADER")
        return
    header = rawpacket[:headerfindresult]
    logging.info("HEADER: " + header)
    datacontent = rawpacket[headerfindresult + 1:]

    if len(datacontent) == 0:
        logging.info("EMPTY BODY")
        return

    logging.info("BODY: " + datacontent)
    decode(datacontent)


def checksum(body):
    global sum1
    logging.debug(body[0:-7])
    sum1 = sum([ord(x) for x in body[0:-7]])
    sum1 %= 128
    logging.debug('CHECKOUT :' + chr(sum1) + ";")
    return chr(sum1) == body[-7]


def decode(body):
    logging.debug(body[-5:-1])
    logging.debug(body[0:2])
    if body[0:2] == 'TJ' and body[-5:-1] == '\\r\\n' and checksum(body):
        logging.debug('VALID MESSAGE')
        logging.debug(body[4:-7])
        modules[body[2]][body[3]](body[4:-7])
    else:
        logging.debug('INVALID MESSAGE')


def piprint(packet):
    print("FROM APRS: " + str(packet))


def on_startup():
    global modules, m_aprs, m_gps
    # modules = {'A':core,'B':m_aprs,'C':'iridium','D':'housekeeping','E':'log','F':'GPS'}
    m_aprs = {'a': aprs.send, 'b': aprs.dump}
    m_gps = {'a': gps.sendgpsthruaprs}
    modules = {'B': m_aprs, 'F': m_gps}
    # core = {}
