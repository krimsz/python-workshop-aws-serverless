import logging
import os

LOG_LEVEL=os.getenv("LOG_LEVEL","INFO")
logger = logging.getLogger('root')
logger.setLevel(LOG_LEVEL)
