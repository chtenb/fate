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

    def partition_content(self, partition):
        """Return the content of the intervals contained in the partition,
        tupled with a boolean indicating wether the interval is in the original selection"""
        return [(self._text[beg:end], in_selection) for (beg, end), in_selection in partition]

    def selection_content(self, selection):
        """Return the content of the intervals contained in the selection"""
        return [self._text[beg:end] for (beg, end) in selection]

    def apply_operation(self, operation):
        """Apply the operation to the text"""
        result = []
        count = 0
        for interval_content, in_selection in self.partition_content(operation.old_selection.partition(self)):
            if in_selection:
                result.append(operation.new_content[count])
                count += 1
            else:
                result.append(interval_content)
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
