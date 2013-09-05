"""A session represents the state of an editing session"""
from .event import Event
from .selection import Selection
import logging

session_list = []

class Session():
    """Class containing all objects of one file editing session"""
    # E.g. text, selection, undo tree, jump history
    OnSessionInit = Event()
    OnApplyOperation = Event()
    OnRead = Event()
    OnWrite = Event()

    reduce_mode = False
    extend_mode = False

    def __init__(self, filename=""):
        self.text = ""
        self.filename = filename
        self.selection = Selection(self)
        self.selection.add((0, 0))
        if filename:
            self.read()
        global session_list
        session_list.append(self)
        self.OnSessionInit.fire(self)

    def read(self):
        """Read text from file"""
        if self.filename:
            with open(self.filename, 'r') as fd:
                self.text = fd.read()
            self.OnRead.fire(self)

    def write(self):
        """Write current text to file"""
        if self.filename:
            with open(self.filename, 'w') as fd:
                fd.write(self.text)
            self.OnWrite.fire(self)

    def select(self, selector):
        """Apply the selector to the selection"""
        selection = selector(self.selection, self.text)
        if self.reduce_mode or self.extend_mode:
            if self.reduce_mode:
                self.selection = self.selection.reduce(selection)
            if self.extend_mode:
                self.selection = self.selection.extend(selection)
        else:
            self.selection = selection

    def apply(self, operation):
        """Apply the operation to the text"""
        partition = operation.old_selection.partition()
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
        self.selection = operation.new_selection
        self.OnApplyOperation.fire(self, operation)

    def content(self, selection):
        """Return the content of the selection"""
        return [self.text[beg:end] for beg, end in selection]


# Load the plugins, after defining Session
from . import user
