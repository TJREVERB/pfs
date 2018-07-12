import core
import logging
import sys


logger = logging.getLogger()
if '--debug' in sys.argv or '-d' in sys.argv:
    logger.setLevel(logging.DEBUG)

if __name__ == '__main__':
    core.startup()
