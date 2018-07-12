import logging

def dispatch_command(packet):
    logging.debug("DISPATCH CALLED")
    rawpacket = str(packet)
    logging.info("FROM APRS: "+rawpacket)
    headerfindresult = rawpacket.find(':')
    if headerfindresult == -1:
        logging.info("INCOMPLETE HEADER")
        return
    header = rawpacket[:headerfindresult]
    logging.info("HEADER: "+header)
    datacontent = rawpacket[headerfindresult+1:]

    if len(datacontent) == 0:
        logging.info("EMPTY BODY")
        return
        
    logging.info("BODY: "+datacontent)

def piprint(packet):
    print("FROM APRS: "+str(packet))
