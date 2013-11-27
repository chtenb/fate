"""A session represents the state of an editing session"""
from .event import Event
from .selection import Selection
from .operation import Operation
import logging
import tempfile

logfilename = tempfile.gettempdir() + '/protexted.log'
logging.basicConfig(filename=logfilename, level=logging.DEBUG)

session_list = []
# An enum containing all possible selection modes
select_mode, extend_mode, reduce_mode = "SELECT", "EXTEND", "REDUCE"


class Session():
    """Class containing all objects of one file editing session"""
    # E.g. text, selection, undo tree, jump history
    OnSessionInit = Event()
    OnApplyOperation = Event()
    OnRead = Event()
    OnWrite = Event()

    selection_mode = select_mode
    forall = False

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
            self.OnWrite.fire(self)

    def select(self, selector):
        """Apply the selector to the selection"""
        self.selection = selector(self.selection)

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
        self.OnApplyOperation.fire(self, operation)
        self.selection_mode = select_mode
        self.selection = operation.new_selection
        return operation.new_selection

    def content(self, selection):
        """Return the content of the selection"""
        return [self.text[max(0, beg):min(len(self.text), end)] for beg, end in selection]


# Load the plugins, after defining Session
from . import plugins

logging.info('protexted loaded')
