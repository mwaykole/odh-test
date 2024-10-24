"""Logging functionality.

NOTE:
    Loggable is intended to be inherited and not instantiated directly.
"""

import logging
import os
import sys


class Loggable(object):
    """Class providing logging functionality."""

    handler_counter = 0

    @classmethod
    def create_log(cls, name='log', filename='/tmp/log.log',
                   level='DEBUG', log_format=None, allow_multiple=False):
        """Creates a log object using the Python "logging" module.

        Args:
            name (optional[str]): The reference name for the logging object.
                Defaults to "log".
            filename (optional[str]): Fully-qualified path and filename.
                Defaults to "/tmp/log.log".
            level (optional[str]): The minimum log level. Defaults to "DEBUG".
            allow_multiple (bool): Can multiple logfiles exist?
                Specifies whether to create a new handler or wipe existing
                before creating a new handler.
        Returns:
            A logging object.
        """
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

        cls.handler_counter += 1

        handler_name = "%s%i" % (name, cls.handler_counter)
        _logfh.set_name(handler_name)

        _formatter = logging.Formatter(log_format)
        _logfh.setFormatter(_formatter)

        _level = logging.getLevelName(level)
        _logfh.level = _level

        log.addHandler(_logfh)

        if not allow_multiple:
            log.setLevel(_level)

        return log

    @classmethod
    def add_log(cls, logobj, filename='/tmp/log.log',
                level='INFO', log_format=None):
        """Adds a logfile to the logobj.

        Args:
            logobj (object): A logging object.
            filename (optional[str]): Fully-qualified path and filename.
                Defaults to "/tmp/log.log".
            level (optional[str]): The minimum log level. Defaults to "INFO".
        """
        name = logobj.name
        log = cls.create_log(name=name, filename=filename,
                             level=level, log_format=log_format,
                             allow_multiple=True)

        return log

    @classmethod
    def remove_log(cls, logobj, name=None):
        """Removes a log handler from a logger object.

        Args:
            logobj (object): A logging object.
            name (optional[str]): The name of the log handler to remove.
                If None, will remove all log handlers from the logger.
        """
        if not name:
            for handler in logobj.handlers[:]:
                logobj.removeHandler(handler)
        else:
            for handler in logobj.handlers[:]:
                if handler.get_name() == name:
                    logobj.removeHandler(handler)

    @classmethod
    def show_logs(cls, logobj):
        """Displays a list of log handlers attached to a logging object.

        Args:
            logobj (object): A logging object.
        """
        log_name = logobj.name
        print("Log: ", log_name)
        for handler in logobj.handlers:
            name = handler.get_name()
            filename = handler.baseFilename if handler.stream != sys.stdout else 'sys.stdout'
            level = logging.getLevelName(handler.level)
            print("- %s: %s (%s)" % (name, filename, level))

    @classmethod
    def disable_log_levels(cls, level):
        """Disables level (and lower) across all logs and handlers.

        Args:
            level (str): String name for the top log level to disable.
        """
        logging.disable(logging.getLevelName(level))

    @classmethod
    def reset_log_levels(cls):
        """Resets logs to current handler levels."""
        logging.disable(logging.NOTSET)

    @classmethod
    def set_log_level(cls, log_name, handler_name, level):
        """Sets the log level for a specific handler.

        Args:
            log_name (str): The name of the log.
            handler_name (str): The name of the specific log handler.
            level (str): The string representation of the log level.
        """
        log = logging.getLogger(log_name)

        for handler in log.handlers:
            if handler.name == handler_name:
                level_name = logging.getLevelName(level)
                handler.setLevel(level_name)
                break

    @classmethod
    def set_log_filename(cls, log_name, handler_name, filename):
        """Changes the logfile name for a specific handler.

        Args:
            log_name (str): The name of the log.
            handler_name (str): The name of the specific log handler.
            filename (str): The path/filename to log to.
        """
        filename = os.path.abspath(filename)
        log = logging.getLogger(log_name)
        for handler in log.handlers:
            if handler.name == handler_name:
                handler.close()
                handler.baseFilename = filename
                break

    @classmethod
    def clear_log(cls, log_name, handler_name):
        """Empties an existing log file.

        Args:
            log_name (str): The name of the log.
            handler_name (str): The name of the specific log handler.
        """
        log = logging.getLogger(log_name)
        for handler in log.handlers:
            if handler.name == handler_name:
                handler.close()
                with open(handler.baseFilename, 'r+') as fd:
                    fd.truncate()
