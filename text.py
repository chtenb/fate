"""This module contains the trivial string datastructure."""

class Text(str):

    """
    Text datastructure implemented by a single string.
    Features a preview mechanism allowing to set an operation in preview.
    The string methods __len__, __getitem__, find, rfind, index and rindex
    are reimplemented to take this preview into account.
    """

    def __init__(self, string):
        self.string = string
        self.preview_operation = None

    def __str__(self):
        return self.get_interval(0, len(self))

    def __repr__(self):
        return 'Text("{}")'.format(self)

    def __len__(self):
        operation = self.preview_operation
        if operation != None:
            diff = operation.compute_newselection()[-1][1] - operation.oldselection[-1][1]
            result = len(self.string) + diff
        else:
            result = len(self.string)

        return result

    def __getitem__(self, index):
        if type(index) == slice:
            beg, end = index.start or 0, index.stop or len(self)
            return self.get_interval(beg, end)
        else:
            return self.get_position(index)

    def find(self, sub, start=None, end=None):
        start = start or 0
        end = end or len(self)
        search_space = self[start:end]
        return start + search_space.find(sub)

    def rfind(self, sub, start=None, end=None):
        start = start or 0
        end = end or len(self)
        search_space = self[start:end]
        return start + search_space.rfind(sub)

    def index(self, sub, start=None, end=None):
        start = start or 0
        end = end or len(self)
        search_space = self[start:end]
        return start + search_space.index(sub)

    def rindex(self, sub, start=None, end=None):
        start = start or 0
        end = end or len(self)
        search_space = self[start:end]
        return start + search_space.rindex(sub)

    def __setitem__(self, index, value):
        return NotImplemented

    def __delitem__(self, index):
        return NotImplemented

    def __add__(self, other):
        return NotImplemented

    def get_position(self, pos):
        """Lookup character at the given position."""
        if self.preview_operation != None:
            oldselection = self.preview_operation.oldselection
            newselection = self.preview_operation.compute_newselection()

            for i in range(len(oldselection)):
                beg, end = oldselection[i]
                nbeg, nend = newselection[i]
                lengthdiff = nend - end
                #print(str(beg) + ',' + str(end))
                #print(str(nbeg) + ',' + str(nend))
                #print(lengthdiff)
                if nbeg <= pos < nend:
                    # if pos is part of new content
                    return self.preview_operation.newcontent[i][pos - nbeg]
                elif pos < nbeg:
                    # We know that pos is not part of new content if
                    # current interval is beyond pos
                    lengthdiff = nbeg - beg
                    return self.string[pos - lengthdiff]
            return self.string[pos - lengthdiff]
        return self.string[pos]

    def get_interval(self, beg, end):
        """Lookup string at the given interval."""
        return ''.join(self.get_position(pos) for pos in range(beg, end))

    def get_selection(self, selection):
        """Lookup the list of strings contained in the given selection."""
        return [self.get_interval(beg, end) for beg, end in selection]

    def preview(self, operation):
        """
        Preview an operation.
        NOTE: regular expressions still work with the original string.
        Setting a preview operation only affects __getitem__.
        """
        self.preview_operation = operation

    def apply(self, document, operation):
        """Apply the given operation to the text."""
        self.preview_operation = None

        partition = operation.oldselection.partition(len(self))
        partition_content = [(in_selection, self.string[beg:end])
                             for in_selection, (beg, end) in partition]

        count = 0
        result = []
        for in_selection, string in partition_content:
            if in_selection:
                result.append(operation.newcontent[count])
                count += 1
            else:
                result.append(string)

        document._text = Text(''.join(result))
