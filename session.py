"""A session represents the state of an editing session"""
from .text import Text
from .event import Event
import logging

sessions = []
current = None

class Session():
    """Class containing all objects of one file editing session"""
    # E.g. text, selection, undo tree, jump history
    OnSessionInit = Event()
    OnApplyOperation = Event()
    OnRead = Event()
    OnWrite = Event()

    def __init__(self, filename=""):
        self.text = Text()
        self.filename = filename
        global sessions
        sessions.append(self)
        self.OnSessionInit.fire(self)

    def read(self):
        """Read text from file"""
        if self.filename:
            with open(self.filename, 'r') as fd:
                self.text.set((0, len(self.text)), fd.read())
        self.OnRead.fire()

    def write(self):
        """Write current text to file"""
        if self.filename:
            with open(self.filename, 'w') as fd:
                fd.write(str(self.text))
        self.OnWrite.fire()

    def apply(self, operation):
        """Apply the operation to the text"""
        for i, interval in enumerate(operation.old_selection):
            self.text.set(interval, operation.new_content[i])
        self.OnApplyOperation.fire(operation)

    def undo(self, operation):
        """Reverse the operation"""
        for i, interval in enumerate(operation.new_selection):
            self.text.set(interval, operation.old_content[i])

    def content(self, selection):
        """Return the content of the selection"""
        return [self.text.get(interval) for interval in selection]


# Load the plugins, after defining Session
from . import load_plugins
