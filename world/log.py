"""
File conaining the logging facility for Avenew.

Import the specific logger from any place in the game.
Top-level functions are used and return configured loggers, although
furthering the configuration is still possible.

Example:

>>> from log import gps
>>> # gps here is a singleton logger
>>> gps.info("...")

"""

from datetime import datetime
import logging
import os

class CustomFormatter(logging.Formatter):

    """Special formatter to add hour and minute."""

    def format(self, record):
        """Add special placeholders for shorter messages."""
        now = datetime.now()
        record.hour = now.hour
        record.minute = now.minute
        return logging.Formatter.format(self, record)


loggers = {}

def logger(name):
    """
    Return an existing or new logger.

    The name should be a string like 'gps' to create the child
    logger 'avenew.gps'.  The log file 'logs/{name}.log' will be
    created.

    If the name is specified as an empty string, a main logger is
    created.  It will have the name 'avenew' and will write both
    in the 'logs/main.log' file and to the console (with an INFO
    level).

    """
    if not name:
        address = "main"
        filename = os.path.join("server", "logs", "main.log")
        name = "avenew"
    else:
        address = name
        filename = os.path.join("server", "logs", name + ".log")
        name = "avenew." + name

    if address in loggers:
        return loggers[address]

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    formatter = CustomFormatter(
            "%(hour)02d:%(minute)02d [%(levelname)s] %(message)s")

    # If it's the main logger, create a stream handler
    if name == "avenew":
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        logger.addHandler(handler)

        # Set a FileHandler for error messages
        handler = logging.FileHandler(os.path.join("server", "logs",
                "error.log"), encoding="utf-8")
        handler.setLevel(logging.ERROR)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # Create the file handler
    handler = logging.FileHandler(filename, encoding="utf-8")
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    loggers[address] = logger
    return logger

MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]

WEEKDAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

def get_date_formats():
    """Return the date formats in a dictionary."""
    now = datetime.now()
    formats = {
        "year": now.year,
        "month": MONTHS[now.month - 1],
        "weekday": WEEKDAYS[now.weekday()],
        "day": now.day,
        "hour": now.hour,
        "minute": now.minute,
        "second": now.second,
    }
    return formats

def begin():
    """Log the beginning of the session to every logger."""
    formats = get_date_formats()

    # Message to be sent
    message = "Avenew started on {weekday}, {month} {day}, {year}"
    message += " at {hour:>02}:{minute:>02}:{second:>02}"
    message = message.format(**formats)
    for logger in loggers.values():
        logger.propagate = False
        logger.info(message)
        logger.propagate = True

def end():
    """Log the end of the session to every logger."""
    formats = get_date_formats()

    # Message to be sent
    message = "Avenew stopped on {weekday}, {month} {day}, {year}"
    message += " at {hour:>02}:{minute:>02}:{second:>02}"
    message = message.format(**formats)
    for logger in loggers.values():
        logger.propagate = False
        logger.info(message)
        logger.propagate = True

# Prepare the different loggers
main = logger("")  # Main logger
app = logger("app")  # Main logger
command = logger("command")  # Main logger
