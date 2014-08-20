"""This module contains the trivial string datastructure."""


class Text(str):

    """
    Text datastructure implemented by a single string.
    Features a preview mechanism.
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
            less = sum(len(interval) for interval in operation.old_selection)
            more = sum(len(interval) for interval in operation.compute_new_selection())
            result = len(self.string) - less + more
        else:
            result = len(self.string)

        # Alternative, faster way to compute it
        if operation != None:
            diff = operation.compute_new_selection()[-1][1] - operation.old_selection[-1][1]
            alt_result = len(self.string) + diff
        else:
            alt_result = len(self.string)

        assert alt_result == result
        return result

    def __getitem__(self, index):
        if type(index) == slice:
            beg, end = index.start or 0, index.stop or len(self)
            return self.get_interval(beg, end)
        else:
            return self.get_position(index)

    def __setitem__(self, index, value):
        return NotImplemented

    def __delitem__(self, index):
        return NotImplemented

    def __add__(self, other):
        return NotImplemented

    def get_position(self, pos):
        """Lookup character at the given position."""
        if self.preview_operation != None:
            oldselection = self.preview_operation.old_selection
            newselection = self.preview_operation.compute_new_selection()

            for i in range(len(oldselection)):
                beg, end = oldselection[i]
                nbeg, nend = newselection[i]
                lengthdiff = nend - end
                #print(str(beg) + ',' + str(end))
                #print(str(nbeg) + ',' + str(nend))
                #print(lengthdiff)
                if nbeg <= pos < nend:
                    # if pos is part of new content
                    return self.preview_operation.new_content[i][pos - nbeg]
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
        """Preview an operation."""
        self.preview_operation = operation

    def apply(self, operation):
        """Apply the given operation to the text."""
        self.preview_operation = None

        partition = operation.old_selection.partition(len(self))
        partition_content = [(in_selection, self.string[beg:end])
                             for in_selection, (beg, end) in partition]

        count = 0
        result = []
        for in_selection, string in partition_content:
            if in_selection:
                result.append(operation.new_content[count])
                count += 1
            else:
                result.append(string)

        self.string = ''.join(result)
