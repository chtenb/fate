"""
This module provides logging functionality.
We provide internal access to the logs through a list of records.
We provide external access to the logs through a logfile.
"""
from tempfile import gettempdir
import logging
from logging import FileHandler, Handler

LOG_FILENAME = gettempdir() + '/fate.log'
RECORDS = []


class InternalHandler(Handler):

    def emit(self, record):
        RECORDS.append(record)


logging.basicConfig(level=logging.DEBUG,
                    handlers=[FileHandler(LOG_FILENAME), InternalHandler()],
                    format='%(asctime)s %(levelname)s:%(message)s',
                    datefmt='%H:%M:%S')
