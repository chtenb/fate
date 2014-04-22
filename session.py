"""A session represents the state of an editing session."""
from .event import Event
from .selection import Selection, Interval
from .clipboard import Clipboard
from .undotree import UndoTree
from .interactionstack import InteractionStack
from . import modes

import logging
import tempfile

logfilename = tempfile.gettempdir() + '/fate.log'
logging.basicConfig(filename=logfilename, level=logging.DEBUG)

session_list = []


class Session():

    """Contains all objects of one file editing session"""
    OnSessionInit = Event()
    _text = ''
    saved = True
    selection_mode = modes.SELECT_MODE
    expandtab = False
    tabwidth = 4

    def __init__(self, filename=""):
        self.OnTextChanged = Event()
        self.OnRead = Event()
        self.OnWrite = Event()

        self.clipboard = Clipboard()
        self.undotree = UndoTree(self)
        self.interactionstack = InteractionStack()

        self.filename = filename
        self.selection = Selection(Interval(0, 0))

        if filename:
            self.read()
        session_list.append(self)
        self.OnSessionInit.fire(self)

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
        if filename:
            self.filename = filename
        if self.filename:
            with open(self.filename, 'r') as fd:
                self.text = fd.read()
            self.saved = True
            self.OnRead.fire(self)

    def write(self, filename=None):
        """Write current text to file."""
        if filename:
            self.filename = filename
        if self.filename:
            with open(self.filename, 'w') as fd:
                fd.write(self.text)
            self.saved = True
            self.OnWrite.fire(self)
