import logging

def dispatch_command(packet):
    logging.info("FROM APRS: "+str(packet))
