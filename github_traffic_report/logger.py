import os
import logging


logger = logging.getLogger()
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))

if not logger.hasHandlers():
    logger.addHandler(logging.StreamHandler())
