class Text:
    """Datastructure for text"""
    _string = ""

    def __str__(self):
        return self._string

    def __len__(self):
        return len(self._string)

    def get(self, interval):
        """Get the content of the interval"""
        beg, end = interval
        return self._string[beg:end]

    def set(self, interval, content):
        """Set the content of the interval"""
        beg, end = interval
        self._string = self._string[:beg] + content + self._string[end:]

    def find(self, string, beg=0, end=None):
        """Find first ocurrence of string from beg"""
        if end == None:
            end = len(self)
        return self._string.find(string, beg, end)

    def rfind(self, string, beg=0, end=None):
        """Backwards find first ocurrence of string from beg"""
        if end == None:
            end = len(self)
        return self._string.rfind(string, beg, end)
