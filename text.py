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

    def iterate(self, selection):
        """Iterate over the text yielding pairs (interval, complement),
        where complement is the string that comes after interval
        and does not intersect with selection"""
        selection_len = len(selection)
        text_len = len(self)

        if not selection or selection[0][0] > 0:
            if not selection:
                complement_end = text_len - 1
            else:
                complement_end = selection[0][0]
            yield ("", self._text[:complement_end])

        for i, (beg, end) in enumerate(selection):
            if i + 1 < selection_len:
                complement_end = selection[i + 1][0]
            else:
                complement_end = text_len - 1
            yield (self._text[beg:end], self._text[end:complement_end])

    def get_selection_content(self, selection):
        return [self._text[beg:end] for (beg, end) in selection]

    #def get_interval(self, beg, end):
        #"""Get the interval between beg and end"""
        #return self._text[beg:end]

    #def set_interval(self, beg, end, string):
        #"""Replace the interval between beg and end with string"""
        #self._text = (self._text[:beg]
                      #+ string
                      #+ self._text[end:])

    def apply_operation(self, operation):
        result = []
        end = 0
        for interval, i in enumerate(operation.old_selection):
            new_string = operation.new_content[i]
            beg = interval[0]
            result.append(self._text[end:beg] + new_string)
            end = interval[1]
        result.append(self._text[end:])
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
