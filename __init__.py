"""This module loads all standard plugins and the user script."""
from os.path import expanduser
from sys import path
import logging

# Load standard plugins
from . import filetype_system
from . import undo_system
from . import labeling_system

logging.info('All standard plugins are loaded.')

# Load user script
path_to_user = expanduser('~') + '/.fate/'
try:
    path.insert(0, path_to_user)
except IOError:
    logging.info('No .fate directory is present.')
else:
    # NOTE: How to not except ImportErrors from the imported script?
    import user
    #try:
        #import user
        #logging.info('User script loaded.')
    #except ImportError:
        #logging.info('No user script is present in .fate directory.')

