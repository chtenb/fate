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

    def get_interval(self, beg, end):
        """Get the interval between beg and end"""
        return self._text[max(0, beg):min(len(self), end)]

    def set_interval(self, beg, end, string):
        """Replace the interval between beg and end with string"""
        self._text = (self._text[:max(0, beg)]
                      + string
                      + self._text[min(len(self), end):])

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
