"""A session represents the state of an editing session"""
from .event import Event
from .selection import Selection
import logging
import tempfile
from . import modes

logfilename = tempfile.gettempdir() + '/fate.log'
logging.basicConfig(filename=logfilename, level=logging.DEBUG)

session_list = []


class Session():
    """Class containing all objects of one file editing session"""
    OnSessionInit = Event()
    OnApplyOperation = Event()
    OnRead = Event()
    OnWrite = Event()

    selection_mode = modes.select_mode
    saved = True

    def __init__(self, filename=""):
        self.text = ""
        self.filename = filename
        self.selection = Selection(self)

        if filename:
            self.read()
        global session_list
        session_list.append(self)
        self.OnSessionInit.fire(self)

    def read(self, filename=None):
        """Read text from file"""
        if filename:
            self.filename = filename
        if self.filename:
            with open(self.filename, 'r') as fd:
                self.text = fd.read()
            self.OnRead.fire(self)

    def write(self, filename=None):
        """Write current text to file"""
        if filename:
            self.filename = filename
        if self.filename:
            with open(self.filename, 'w') as fd:
                fd.write(self.text)
            self.saved = True
            self.OnWrite.fire(self)

    def apply(self, actions):
        """Apply an action or a sequence of actions to self"""
        if isinstance(actions, (list, tuple)):
            for action in actions:
                action(self)
        else:
            actions(self)

    def content(self, selection):
        """Return the content of the selection"""
        return [self.text[max(0, beg):min(len(self.text), end)] for beg, end in selection]


# Load the plugins, after defining Session
from . import plugins

logging.info('fate loaded')
