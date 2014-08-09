"""This module defines the class Operation."""
from . import modes
from .actiontools import Undoable
from .selection import Selection, Interval


class Operation(Undoable):

    """
    A container of modified content of a selection.
    Can be inverted such that the operation can be undone by applying the inverse.
    The members are `old_selection`, `old_content`, `new_content`.
    The property `new_selection` is only available after the operation
    has been applied.
    """

    def __init__(self, session, new_content=None, selection=None):
        selection = selection or session.selection
        self.old_selection = selection
        self.old_content = selection.content(session)
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

    def do(self, session):
        """Execute operation."""
        self._apply(session)
        session.mode = modes.SELECT

    def undo(self, session):
        """Undo operation."""
        self._apply(session, inverse=True)

    def _apply(self, session, inverse=False):
        """Apply self to the session."""
        if inverse:
            old_selection = self.compute_new_selection()
            new_selection = self.old_selection
            new_content = self.old_content
        else:
            new_selection = self.compute_new_selection()
            old_selection = self.old_selection
            new_content = self.new_content

        #print(session.text)
        #print('old: ' + str(old_selection))
        #print('new: ' + str(new_selection))

        # Make sure the application of this operation is valid at this moment
        assert old_selection.isvalid(session)
        assert len(new_selection) == len(old_selection)
        assert len(new_content) == len(self.old_content)

        partition = old_selection.partition(session)
        partition_content = [(in_selection, session.text[beg:end])
                             for in_selection, (beg, end) in partition]

        count = 0
        result = []
        for in_selection, string in partition_content:
            if in_selection:
                result.append(new_content[count])
                count += 1
            else:
                result.append(string)

        session.text = ''.join(result)
        session.selection_mode = modes.SELECT
        session.selection = new_selection

