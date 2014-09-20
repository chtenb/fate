"""
This module loads fate by loading all standard plugins and the user script.
This makes sure that all code that depends on these won't have to import them manually.
"""
from . import log
from logging import info, debug


info('Starting fate.')

# Load modules exposing commands, to make sure the commands module contains all commands
from . import (clipboard, commandmode, commandtools, document, filecommands,
               insertoperations, operators, repeat, search, selectors, undotree, pointer)

# Load standard plugins
from . import filetype_system
from . import labeling_system

info('All standard plugins are loaded.')


# Load user script if existent
from os.path import expanduser
from sys import path
from importlib import find_loader

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
        doc.processinput(userinput)
