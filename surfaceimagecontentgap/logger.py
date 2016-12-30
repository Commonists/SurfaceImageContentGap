import logging
import sys


FMT = '%(asctime)s    %(module)s    %(levelname)s    %(message)s'
LOGGER_NAME = 'sicglog'


def logger(debug=False):
    """Logger for query engine."""
    log = logging.getLogger(name=LOGGER_NAME)
    if not len(log.handlers):
        # handlers have not yet been added
        setup(log, debug=debug)
    return log


def setup(log, debug=True):
    consolehandler = logging.StreamHandler(stream=sys.stdout)
    formatter = logging.Formatter(FMT)
    consolehandler.setFormatter(formatter)
    if debug:
        consolehandler.setLevel(logging.DEBUG)
        log.addHandler(consolehandler)
        log.setLevel(logging.DEBUG)
    else:
        consolehandler.setLevel(logging.INFO)
        log.addHandler(consolehandler)
        log.setLevel(logging.INFO)
