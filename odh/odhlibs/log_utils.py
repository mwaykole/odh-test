import logging
import os
import sys

# Global variable to keep track of handler count
handler_counter = 0


def create_log(name='log', filename='/tmp/log.log',
               level='DEBUG', log_format=None, allow_multiple=False):
    global handler_counter

    if not log_format:
        log_format = ('%(asctime)s %(levelname)s '
                      '(%(funcName)s) %(message)s')
    log = logging.getLogger(name)
    log.propagate = False
    _logfile = filename

    if not os.path.exists(_logfile):
        _logdir = os.path.dirname(_logfile)
        if not os.path.exists(_logdir):
            os.makedirs(_logdir)

    if not allow_multiple:
        for handler in log.handlers[:]:
            log.removeHandler(handler)

    if filename == 'STDOUT':
        _logfh = logging.StreamHandler(sys.stdout)
    else:
        _logfh = logging.FileHandler(_logfile)

    handler_counter += 1

    handler_name = "%s%i" % (name, handler_counter)
    _logfh.set_name(handler_name)

    _formatter = logging.Formatter(log_format)
    _logfh.setFormatter(_formatter)

    _level = logging.getLevelName(level)
    _logfh.level = _level

    log.addHandler(_logfh)

    if not allow_multiple:
        log.setLevel(_level)

    return log

# Other functions (add_log, remove_log, etc.) should be included here as well
