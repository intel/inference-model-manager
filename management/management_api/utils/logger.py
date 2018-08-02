import logging
import os


def get_logger(name):
    logger = logging.getLogger(name)
    logging_level = os.getenv('LOG_LEVEL', 'INFO')
    logger.setLevel(logging_level)
    logging.basicConfig(level=logging_level)
    return logger
