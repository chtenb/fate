"""A session represents the state of an editing session"""
from .text import Text
from .event import Event
import logging

sessions = []
current = None

class Session():
    """Class containing all objects of one file editing session"""
    # E.g. text, selection, undo tree, jump history
    OnInit = Event()

    def __init__(self, filename=""):
        self.text = Text()
        self.filename = filename

        self.OnInit.fire(self)

        global sessions
        sessions.append(self)

    def read(self):
        """Read text from file"""
        if self.filename:
            with open(self.filename, 'r') as fd:
                self.text.set((0, len(self.text)), fd.read())

    def write(self):
        """Write current text to file"""
        if self.filename:
            with open(self.filename, 'w') as fd:
                fd.write(str(self.text))

# Load the plugins, after defining Session
from . import plugin_dependencies
