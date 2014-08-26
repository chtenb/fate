"""
This module loads fate by loading all standard plugins and the user script.
This makes sure that all code that depends on these won't have to import them manually.
"""
from os.path import expanduser
from sys import path
from importlib import find_loader
from tempfile import gettempdir
from queue import Queue
import logging
from logging.handlers import QueueHandler, QueueListener
from logging import FileHandler, info, debug

# We provide internal access to the logs through a queue
# To be accessed by a QueueListener
LOG_QUEUE = Queue()
queue_handler = QueueHandler(LOG_QUEUE)

# We provide external access to the logs through a logfile
LOG_FILENAME = gettempdir() + '/fate.log'
file_handler = FileHandler(LOG_FILENAME)

logging.basicConfig(level=logging.DEBUG,
                    handlers=[file_handler, queue_handler],
                    format='%(asctime)s %(levelname)s:%(message)s',
                    datefmt='%H:%M:%S')


info('Starting fate.')

# Load modules exposing commands, to make sure the commands module contains all commands
from . import (clipboard, commandmode, commandtools, document, insertoperations,
               operators, repeat, search, selectors, undotree)

# Load standard plugins
from . import filetype_system
from . import labeling_system

info('All standard plugins are loaded.')


# Load user script if existent
path_to_user = expanduser('~') + '/.fate/'
try:
    path.insert(0, path_to_user)
except IOError:
    info('No .fate directory is present.')
else:
    if find_loader('user'):
        import user
        info('User script loaded.')
    else:
        info('No user script is present in .fate directory.')


# Expose main loop function to the userinterface
def run():
    """Main input loop for fate."""
    while document.activedocument != None:
        doc = document.activedocument
        doc.ui.touch()
        userinput = doc.ui.getinput()

        # If the cancel key has been pressed, convert input to Cancel
        if userinput == doc.cancelkey:
            userinput = 'Cancel'

        debug('Input: ' + str(userinput))

        if doc.mode:
            # We are not in normalmode
            doc.mode.peek().processinput(doc, userinput)
        else:
            # We are in normalmode
            if type(userinput) == str:
                key = userinput
                if key in doc.keymap:
                    command = doc.keymap[key]
                else:
                    command = None
            else:
                command = userinput

            while callable(command):
                command = command(doc)
