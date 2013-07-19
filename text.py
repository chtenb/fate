from selectors import partition

class Text:
    """Class representing instance of a text file"""

    def __init__(self, file_name, eol_char='\n'):
        self._file_name = file_name
        self.eol_char = eol_char
        self.read()

    def __str__(self):
        return self._text

    def __len__(self):
        return len(self._text)

    def read(self):
        """Read text from file"""
        file_descriptor = open(self._file_name, 'r')
        self._text = file_descriptor.read()
        file_descriptor.close()

    def write(self):
        """Write current text to file"""
        file_descriptor = open(self._file_name, 'w')
        file_descriptor.write(str(self))
        file_descriptor.close()

    def selection_content(self, selection):
        """Return the bounded content of the intervals contained in the selection"""
        return [self.interval_content(interval) for interval in selection]

    def interval_content(self, interval):
        """Return the content of the interval"""
        beg, end = interval
        return self._text[beg:end]

    def apply_operation(self, operation):
        """Apply the operation to the text"""
        result = []
        count = 0
        for interval in partition(operation.old_selection, self):
            if interval in operation.old_selection:
                result.append(operation.new_content[count])
                count += 1
            else:
                result.append(self.interval_content(interval))
        self._text = "".join(result)

    def find(self, string, beg=0, end=None):
        """Find first ocurrence of string from beg"""
        if end == None:
            end = len(self)
        return self._text.find(string, beg, end)

    def rfind(self, string, beg=0, end=None):
        """Backwards find first ocurrence of string from beg"""
        if end == None:
            end = len(self)
        return self._text.rfind(string, beg, end)
