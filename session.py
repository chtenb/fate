"""A session represents the state of an editing session."""
from .event import Event
from .selection import Selection
from .clipboard import Clipboard
from .action import ActionTree
from . import modes

import logging
import tempfile

logfilename = tempfile.gettempdir() + '/fate.log'
logging.basicConfig(filename=logfilename, level=logging.DEBUG)

session_list = []


class Session():
    """Contains all objects of one file editing session"""
    OnSessionInit = Event()
    OnApplyOperation = Event()
    OnApplyActor = Event()
    OnRead = Event()
    OnWrite = Event()

    clipboard = Clipboard()
    actiontree = ActionTree()

    selection = None
    selection_mode = modes.SELECT_MODE
    saved = True

    def __init__(self, filename=""):
        self.text = ""
        self.filename = filename
        self.selection = Selection(self)

        if filename:
            self.read()
        session_list.append(self)
        self.OnSessionInit.fire(self)

    def read(self, filename=None):
        """Read text from file."""
        if filename:
            self.filename = filename
        if self.filename:
            with open(self.filename, 'r') as fd:
                self.text = fd.read()
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

    def content(self, selection):
        """Return the content of the selection."""
        return [self.text[max(0, beg):min(len(self.text), end)] for beg, end in selection]

