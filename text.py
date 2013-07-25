class Text:
    """Datastructure for text"""
    _chars = []

    def __str__(self):
        return self._chars

    def __len__(self):
        return len(self._chars)

    def get(self, interval):
        """Get the content of the interval"""
        beg, end = interval
        return self._chars[beg:end]

    def set(self, interval, content):
        """Set the content of the interval"""
        beg, end = interval
        self._chars = self._chars[:beg] + content + self._chars[end:]

    def find(self, string, beg=0, end=None):
        """Find first ocurrence of string from beg"""
        if end == None:
            end = len(self)
        return self._chars.find(string, beg, end)

    def rfind(self, string, beg=0, end=None):
        """Backwards find first ocurrence of string from beg"""
        if end == None:
            end = len(self)
        return self._chars.rfind(string, beg, end)
