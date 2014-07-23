"""A session represents the state of an editing session."""
from .event import Event
from .selection import Selection, Interval
from .clipboard import Clipboard
from .undotree import UndoTree
from . import modes

import logging

session_list = []


class Session():

    """Contains all objects of one file editing session"""
    OnSessionInit = Event()
    _text = ''
    saved = True
    mode = modes.SELECT
    expandtab = False
    tabwidth = 4
    search_pattern = ''

    def __init__(self, filename=""):
        session_list.append(self)
        self.OnTextChanged = Event()
        self.OnRead = Event()
        self.OnWrite = Event()
        self.OnQuit = Event()

        self.clipboard = Clipboard()
        self.undotree = UndoTree(self)

        self.filename = filename
        self.selection = Selection(Interval(0, 0))
        self.locked_selection = None
        self.ui = None

        # Load the default key map
        from .keymap import default
        self.keymap = {}
        self.keymap.update(default)

        self.OnSessionInit.fire(self)
        if filename:
            self.read()

    def quit(self):
        """Quit session."""
        logging.info('Quitting session ' + str(self))
        self.OnQuit.fire(self)
        session_list.remove(self)

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
