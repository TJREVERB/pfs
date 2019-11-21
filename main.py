#!/usr/bin/env python3
import logging
import sys

from core.core import Core

logger = logging.getLogger()
if '--debug' in sys.argv or '-d' in sys.argv:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

if __name__ == '__main__':
    logging.info("Starting application")
    c = Core()
    c.start()
