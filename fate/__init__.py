"""
This module loads fate by loading all standard plugins and the user script.
This makes sure that all code that depends on these won't have to import them manually.
"""

# Initialize logger
from . import log
from logging import info, debug

info('Starting fate.')

import os
import sys

# Make sure packages from submodules can be imported
typedecorator_path = (os.path.dirname(os.path.abspath(__file__))
                      + os.sep + '..' + os.sep + 'typedecorator')
debug('Adding {} to path'.format(typedecorator_path))
sys.path.insert(0, typedecorator_path)
import typedecorator
typedecorator.setup_typecheck()


class CommandsSingleton:
    """
    This is a singleton which should contain all commands that are available to the user.
    A completion engine can use this to compute completions.

    The goal of a text editor is to make modifications to a text.
    More generally, the user should also be able to modify things other
    than text, such as options or other meta stuff.
    We store all relevant data for editing a text in a single object,
    and call this object a document.

    To make modifications to a document, we define commands.
    An command is callable object that can make a modification to a document.
    An command must therefore accept a document as first argument, which must also be
    the only required argument.

    Commands must be stateless, that is why they be be shared among documents.
    Commands have their name automatically available via __name__ after they are added
    to this singleton.

    In many cases it is useful to create commands on the fly.
    Callable objects that create and return commands are called 'command constructors'.
    A special type of command constructors are those that require a document as argument.
    Let us call these 'actors'.
    It is a convention whenever commands are executed and the returned result
    is callable, it is treated like a command and called recursively.
    """

    def __set__(self, instance, value):
        raise ValueError("Trying to assign to static singleton commands.")

    def __setattr__(self, name, command):
        if not callable(command):
            raise ValueError("A command must be callable.")
        command.__name__ = name
        object.__setattr__(self, name, command)

commands = CommandsSingleton()


# Load modules exposing commands, to make sure the commands module contains all core
# commands
from . import (clipboard, commandmode, commandtools, completer, document, filecommands,
               insertoperations, operators, repeat, search, selecting,
               undotree, pointer, prompt)

# Load standard plugins
from . import formatting
from . import errorchecking
from . import highlighting
from . import filetype

# Load view functionality
from . import conceal, textview


from . import normalmode

# TODO: why doesn't pylint recognize functions in the commands module
info('All standard plugins are loaded.')


# Load user script if existent
from os.path import expanduser
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
        doc.ui.touch()
        userinput = doc.ui.getinput()
        doc.processinput(userinput)
