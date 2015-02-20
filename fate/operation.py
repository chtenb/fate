"""This module defines the class Operation."""
from .commandtools import Undoable
from .selection import Selection, Interval


class Operation(Undoable):

    """
    A container of modified content of a selection.
    Can be inverted such that the operation can be undone by applying the inverse.
    The members are `oldselection`, `old_content`, `newcontent`.
    The property `newselection` is only available after the operation
    has been applied.
    """

    def __init__(self, document, newcontent=None, selection=None):
        selection = selection or document.selection
        self.oldselection = selection
        self.old_content = selection.content(document)
        try:
            self.newcontent = newcontent or self.old_content[:]
        except AttributeError:
            # newcontent has been overriden
            # TODO neater fix for this
            pass

    def __str__(self):
        attributes = [('oldselection', self.oldselection),
                      ('computed newselection', self.compute_newselection()),
                      ('old_content', self.old_content),
                      ('newcontent', self.newcontent)]
        return '\n'.join([k + ': ' + str(v) for k, v in attributes])

    def compute_newselection(self):
        """The selection containing the potential result of the operation."""
        beg = self.oldselection[0][0]
        end = beg + len(self.newcontent[0])
        result = Selection(Interval(beg, end))
        for i in range(1, len(self.oldselection)):
            beg = end + self.oldselection[i][0] - self.oldselection[i - 1][1]
            end = beg + len(self.newcontent[i])
            result.add(Interval(beg, end))
        return result

    def do(self, document):
        """Execute operation."""
        self._apply(document)

    def undo(self, document):
        """Undo operation."""
        self._apply(document, inverse=True)

    def _apply(self, document, inverse=False):
        """Apply self to the document."""
        if inverse:
            oldselection = self.compute_newselection()
            newselection = self.oldselection
            newcontent = self.old_content
        else:
            newselection = self.compute_newselection()
            oldselection = self.oldselection
            newcontent = self.newcontent

        #print(document.text)
        #print('old: ' + str(oldselection))
        #print('new: ' + str(newselection))

        # Make sure the application of this operation is valid at this moment
        oldselection.validate(document)
        assert len(newselection) == len(oldselection)
        assert len(newcontent) == len(self.old_content)

        partition = oldselection.partition(document)
        partition_content = [(in_selection, document.text[beg:end])
                             for in_selection, (beg, end) in partition]

        count = 0
        result = []
        for in_selection, string in partition_content:
            if in_selection:
                result.append(newcontent[count])
                count += 1
            else:
                result.append(string)

        document.text = ''.join(result)
        document.selection = newselection

