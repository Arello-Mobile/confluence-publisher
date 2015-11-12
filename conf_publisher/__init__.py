import logging
import sys


def get_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Console Handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)

    formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(module)s %(process)d %(thread)d] %(message)s')
    ch.setFormatter(formatter)

    logger.addHandler(ch)

    return logger


log = get_logger()
