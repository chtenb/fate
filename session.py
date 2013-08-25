"""A session represents the state of an editing session"""
from .event import Event
from . import current
import logging


class Session():
    """Class containing all objects of one file editing session"""
    # E.g. text, selection, undo tree, jump history
    OnSessionInit = Event()
    OnApplyOperation = Event()
    OnRead = Event()
    OnWrite = Event()

    def __init__(self, filename=""):
        self.text = ""
        self.filename = filename
        if filename:
            self.read()
        current.sessions.append(self)
        self.OnSessionInit.fire(self)

    def read(self):
        """Read text from file"""
        if self.filename:
            with open(self.filename, 'r') as fd:
                self.text = fd.read()
        self.OnRead.fire()

    def write(self):
        """Write current text to file"""
        if self.filename:
            with open(self.filename, 'w') as fd:
                fd.write(self.text)
        self.OnWrite.fire()

    def apply(self, operation):
        """Apply the operation to the text"""
        partition = operation.old_selection.partition(self.text)
        partition_content = [(in_selection, self.text[beg:end]) for in_selection, (beg, end) in partition]
        count = 0
        result = []
        for in_selection, string in partition_content:
            if in_selection:
                result.append(operation.new_content[count])
                count += 1
            else:
                result.append(string)

        self.text = ''.join(result)
        self.OnApplyOperation.fire(operation)

    def undo(self, operation):
        """Apply the operation reversely"""
        self.apply(operation.inverse())

    def content(self, selection):
        """Return the content of the selection"""
        return [self.text[beg:end] for beg, end in selection]


from . import user
# Load the plugins, after defining Session
#from . import load_plugins
