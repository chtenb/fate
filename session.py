"""Singleton containing all editing sessions"""

from text import Text
from selection import Selection

sessions = []
current = None

class Session():
    """Class containing all objects of one file editing session"""
    # E.g. text, selection, undo tree, jump history
    _text = Text()
    selection = Selection()

    def __init__(self, file_name=""):
        self.file_name = file_name
        global sessions
        sessions.append(self)
        self.read()

    def read(self):
        """Read text from file"""
        if self.file_name:
            with open(self.file_name, 'r') as fd:
                self._text.set((0, len(self._text)), fd.read())

    def write(self):
        """Write current text to file"""
        if self.file_name:
            with open(self.file_name, 'w') as fd:
                fd.write(str(self._text))

    def selection_content(self, selection):
        """Return the content of the intervals contained in the selection"""
        return [self._text.get(interval) for interval in selection]

    def apply_operation(self, operation):
        """Apply the operation to the text"""
        for i, interval in enumerate(operation.old_selection):
            self._text.set(interval, operation.new_content[i])
