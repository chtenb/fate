"""
This module loads fate by loading all standard plugins and the user script.
This makes sure that all code that depends on these won't have to import them manually.
"""
from os.path import expanduser
from sys import path
from importlib import find_loader
import logging


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

