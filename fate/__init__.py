"""
This module loads fate by loading all standard plugins and the user script.
This makes sure that all code that depends on these won't have to import them manually.
"""

# Initialize logger
from . import log
from logging import info


info('Starting fate.')

# Load modules exposing commands, to make sure the commands module contains all core
# commands
from . import commands
from . import (clipboard, commandmode, commandtools, completer, document, filecommands,
               insertoperations, operators, repeat, search, selecting,
               undotree, pointer)

# Load standard plugins
from . import formatting
from . import errorchecking
from . import highlighting
from . import filetype
from . import view

from . import normalmode

# TODO: why doesn't pylint recognize functions in the commands module
info('All standard plugins are loaded.')


# Load user script if existent
from os.path import expanduser
import sys
from importlib import find_loader, import_module

path_to_user = expanduser('~') + '/.fate/'
try:
    sys.path.insert(0, path_to_user)
except IOError:
    info('No .fate directory is present.')
else:
    try:
        import user
    except ImportError as e:
        # Catch import error non-recursively
        if e.name == 'user':
            info('No user script is present in .fate directory.')
        else:
            raise
    else:
        info('User script loaded.')


# Expose main loop function to the userinterface
def run():
    """Main input loop for fate."""
    while document.activedocument != None:
        doc = document.activedocument
        doc.view.refresh()
        doc.ui.touch()
        userinput = doc.ui.getinput()
        doc.processinput(userinput)
