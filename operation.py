"""This module defines the class Operation."""
from .commandtools import Undoable
from .selection import Selection, Interval


class Operation(Undoable):

    """
    A container of modified content of a selection.
    Can be inverted such that the operation can be undone by applying the inverse.
    The members are `old_selection`, `old_content`, `new_content`.
    The property `new_selection` is only available after the operation
    has been applied.
    """

    def __init__(self, document, new_content=None, selection=None):
        selection = selection or document.selection
        self.old_selection = selection
        self.old_content = selection.content(document)
        try:
            self.new_content = new_content or self.old_content[:]
        except AttributeError:
            # new_content has been overriden
            # TODO neater fix for this
            pass

    def __str__(self):
        attributes = [('old_selection', self.old_selection),
                      ('computed new_selection', self.compute_new_selection()),
                      ('old_content', self.old_content),
                      ('new_content', self.new_content)]
        return '\n'.join([k + ': ' + str(v) for k, v in attributes])

    def compute_new_selection(self):
        """The selection containing the potential result of the operation."""
        beg = self.old_selection[0][0]
        end = beg + len(self.new_content[0])
        result = Selection(Interval(beg, end))
        for i in range(1, len(self.old_selection)):
            beg = end + self.old_selection[i][0] - self.old_selection[i - 1][1]
            end = beg + len(self.new_content[i])
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
            old_selection = self.compute_new_selection()
            new_selection = self.old_selection
            new_content = self.old_content
        else:
            new_selection = self.compute_new_selection()
            old_selection = self.old_selection
            new_content = self.new_content

        #print(document.text)
        #print('old: ' + str(old_selection))
        #print('new: ' + str(new_selection))

        # Make sure the application of this operation is valid at this moment
        assert old_selection.isvalid(document)
        assert len(new_selection) == len(old_selection)
        assert len(new_content) == len(self.old_content)

        document.text.apply(self)
        document.selection = new_selection
        document.OnTextChanged.fire(document)

