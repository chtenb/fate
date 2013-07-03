class Text:
    """Class representing instance of a text file"""

    def __init__(self, file_name):
        self._file_name = file_name

    def __enter__(self):
        self.read()
        return self

    def __exit__(self, type, value, traceback):
        pass

    def __str__(self):
        return self._text

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

    def get_interval(self, start, end):
        """Get the interval specified by arguments"""
        return self._text[max(0, start):min(len(self._text), end)]

    def set_interval(self, start, end, string):
        """Set the interval specified by arguments"""
        self._text = (self._text[:max(0, start - 1)]
                      + string
                      + self._text[min(len(self._text), end + 1):])
