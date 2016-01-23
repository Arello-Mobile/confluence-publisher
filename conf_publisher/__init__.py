import sys
import logging

log = logging.getLogger(__name__)


def setup_logger(level, stream=None):
    levels = [logging.WARNING, logging.INFO, logging.DEBUG]

    if level is None:
        level = 0
    elif level >= len(levels):
        level = len(levels) - 1

    if stream is None:
        stream = sys.stderr

    log.setLevel(levels[level])
    log.addHandler(logging.StreamHandler(stream))