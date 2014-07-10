"""
This module loads fate by loading all standard plugins and the user script.
This makes sure that all code that depends on these won't have to import them manually.
"""
from os.path import expanduser
from sys import path
from importlib import find_loader
import logging
import tempfile
from queue import Queue
from logging.handlers import QueueHandler, QueueListener
from logging import FileHandler

# We provide internal access to the logs through a queue
# To be accessed by a QueueListener
LOG_QUEUE = Queue()
queue_handler = QueueHandler(LOG_QUEUE)

# We provide external access to the logs through a logfile
LOG_FILENAME = tempfile.gettempdir() + '/fate.log'
file_handler = FileHandler(LOG_FILENAME)

logging.basicConfig(level=logging.DEBUG,
                    handlers=[file_handler, queue_handler],
                    format='%(asctime)s %(levelname)s:%(message)s',
                    datefmt='%H:%M:%S')


logging.info('Starting fate.')

# Load modules exposing actions, to make sure the actions module contains all actions
from . import actions, selectors, operators, clipboard, compoundactions, uiactions, modes

# Load standard plugins
from . import filetype_system
from . import labeling_system

logging.info('All standard plugins are loaded.')


# Load user script if existent
path_to_user = expanduser('~') + '/.fate/'
try:
    path.insert(0, path_to_user)
except IOError:
    logging.info('No .fate directory is present.')
else:
    if find_loader('user'):
        import user
        logging.info('User script loaded.')
    else:
        logging.info('No user script is present in .fate directory.')
