"""A session represents the state of an editing session."""
from .event import Event
from .selection import Selection, Interval
from .clipboard import Clipboard
from .undotree import UndoTree
from . import modes
from .userinterface import UserInterface
from collections import deque

import logging

sessionlist = []


class Session():

    """Contains all objects of one file editing session"""
    OnSessionInit = Event()
    UserInterfaceClass = None
    _text = ''
    saved = True
    mode = modes.SELECT
    expandtab = False
    tabwidth = 4
    autoindent = True
    search_pattern = ''
    last_repeatable_action = None
    locked_selection = None

    def __init__(self, filename=""):
        sessionlist.append(self)
        self.OnTextChanged = Event()
        self.OnRead = Event()
        self.OnWrite = Event()
        self.OnQuit = Event()
        self.OnUserInput = Event()

        self.clipboard = Clipboard()
        self.undotree = UndoTree(self)

        self.filename = filename
        self.selection = Selection(Interval(0, 0))
        self.food = deque()

        if not self.UserInterfaceClass:
            raise Exception('No userinterface class specified in Session.UserInterfaceClass.')
        if not issubclass(self.UserInterfaceClass, UserInterface):
            raise Exception('Session.UserInterfaceClass not a subclass of UserInterface.')

        self.ui = self.UserInterfaceClass(self)
        self.OnQuit.add(self.ui.quit)

        # Load the default key map
        from .keymap import default
        self.keymap = {}
        self.keymap.update(default)

        self.OnSessionInit.fire(self)

        if filename:
            self.read()

    def getchar(self):
        if self.food:
            char = self.food.popleft()
        else:
            char = self.ui.getchar()
        self.OnUserInput.fire(self, char)
        return char

    def feed(self, chars):
        self.food.extend(chars)

    def quit(self):
        """Quit session."""
        logging.info('Quitting session ' + str(self))
        self.OnQuit.fire(self)
        sessionlist.remove(self)

    @property
    def selection(self):
        return self._selection

    @selection.setter
    def selection(self, value):
        # Make sure only valid selections are applied
        assert isinstance(value, Selection) and value.isvalid(self)
        self._selection = value

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        self.saved = False
        self.OnTextChanged.fire(self)

    def read(self, filename=None):
        """Read text from file."""
        filename = filename or self.filename

        if filename:
            try:
                with open(filename, 'r') as fd:
                    self.text = fd.read()
                self.saved = True
                self.OnRead.fire(self)
            except (FileNotFoundError, PermissionError) as e:
                logging.error(str(e))
        else:
            logging.error('No filename')

    def write(self, filename=None):
        """Write current text to file."""
        filename = filename or self.filename

        if filename:
            try:
                with open(filename, 'w') as fd:
                    fd.write(self.text)
                self.saved = True
                self.OnWrite.fire(self)
            except (FileNotFoundError, PermissionError) as e:
                logging.error(str(e))
        else:
            logging.error('No filename')
