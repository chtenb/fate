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
    file_name = ""

    def __init__(self, file_name):
        self.file_name = file_name
        self.read()
        global sessions
        session.append(self)

    def read(self):
        """Read text from file"""
        file_descriptor = open(self._file_name, 'r')
        self._text.set((0, len(self._text)), file_descriptor.read())
        file_descriptor.close()

    def write(self):
        """Write current text to file"""
        file_descriptor = open(self._file_name, 'w')
        file_descriptor.write(str(self))
        file_descriptor.close()

    def selection_content(self, selection):
        """Return the content of the intervals contained in the selection"""
        return [self._text.get(interval) for interval in selection]

    def apply_operation(self, operation):
        """Apply the operation to the text"""
        for i, interval in enumerate(operation.old_selection):
            self._text.set(interval, operation.new_content[i])
