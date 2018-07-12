import core
import logging
import sys


logger = logging.getLogger()
if '--debug' in sys.argv or '-d' in sys.argv:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

if __name__ == '__main__':
    logging.info("Starting application")
    core.startup()
