import logging

def dispatch_command(packet):
    logging.info("FROM APRS: "+str(packet))

def piprint(packet):
    print("FROM APRS: "+str(packet))
