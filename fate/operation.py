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

    def __init__(self, doc, newcontent, selection=None):
        selection = selection or doc.selection
        self.oldselection = selection
        self.old_content = selection.content(doc)
        self.newcontent = newcontent

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

    def do(self, doc):
        """Execute operation."""
        self._apply(doc)

    def undo(self, doc):
        """Undo operation."""
        self._apply(doc, inverse=True)

    def _apply(self, doc, inverse=False):
        """Apply self to the doc."""
        if inverse:
            oldselection = self.compute_newselection()
            newselection = self.oldselection
            newcontent = self.old_content
        else:
            newselection = self.compute_newselection()
            oldselection = self.oldselection
            newcontent = self.newcontent

        # Make sure the application of this operation is valid at this moment
        oldselection.validate(doc)
        assert len(newselection) == len(oldselection)
        assert len(newcontent) == len(self.old_content)

        partition = oldselection.partition(doc)
        partition_content = [(in_selection, doc.text[beg:end])
                             for in_selection, (beg, end) in partition]

        count = 0
        result = []
        for in_selection, string in partition_content:
            if in_selection:
                result.append(newcontent[count])
                count += 1
            else:
                result.append(string)

        doc.text = ''.join(result)
        doc.selection = newselection

