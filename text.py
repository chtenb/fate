"""This module contains the trivial string datastructure."""


class Text:

    """
    Text datastructure implemented by a single string.
    We feature a preview mechanism.
    """

    def __init__(self, string):
        self.string = string
        self.preview_operation = None

    @property
    def length(self):
        # TODO: take preview_operation into account
        return len(self.string)

    def __len__(self):
        # TODO: this one is obsolete
        return self.length

    def get(self, pos):
        """Lookup character at the given position."""
        if self.preview_operation != None:
            for beg, end in self.preview_operation.new_selection:
                if beg <= pos < end:
                    return self.preview_operation.new_content[pos - beg]
        return self.string[pos]

    def get_interval(self, beg, end):
        """Lookup string at the given interval."""
        return ''.join(self.get(pos) for pos in range(beg, end))

    def tostring(self):
        """Return the entire text as a string."""
        return self.get_interval(0, self.length)


    # def get(self, selection):
        #"""Lookup the list of strings contained in the given selection."""
        # if self.preview_operation != None:
            # pass
        # else:
            # return [self.string[beg:end] for beg, end in selection]

    def preview(self, operation):
        """Preview an operation."""
        self.preview_operation = operation

    def apply(self, operation):
        """Apply the given operation to the text."""
        self.preview_operation = None

        partition = operation.old_selection.partition(self.length)
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
