"""This module defines the class Operation."""
from .selection import Selection
from . import modes
import copy


class Operation:
    """A container of modified content of a selection.
    Can be inverted such that the operation can be undone by applying the inverse.
    The members are `old_selection`, `old_content`, `new_content` and `new_selection`.
    """

    def __init__(self, selection, new_content=None):
        self.session = selection.session
        self.old_selection = selection
        self.old_content = self.session.content(selection)
        self.new_content = new_content or self.old_content[:]

    @property
    def new_selection(self):
        """The selection containing the potential result of the operation."""
        beg = self.old_selection[0][0]
        end = beg + len(self.new_content[0])
        result = Selection(self.session, [(beg, end)])
        for i in range(1, len(self.old_selection)):
            beg = end + self.old_selection[i][0] - self.old_selection[i - 1][1]
            end = beg + len(self.new_content[i])
            result.add((beg, end))
        return result

    def inverse(self):
        """Return the inverse operation of self."""
        result = copy.copy(self)
        result.old_selection = self.new_selection
        result.old_content, result.new_content = result.new_content, result.old_content
        return result

    def do(self):
        """Apply self to the session."""
        session = self.session
        partition = self.old_selection.partition()
        partition_content = [(in_selection, session.text[beg:end])
                             for in_selection, (beg, end) in partition]
        count = 0
        result = []
        for in_selection, string in partition_content:
            if in_selection:
                result.append(self.new_content[count])
                count += 1
            else:
                result.append(string)

        session.text = ''.join(result)
        session.saved = False
        session.OnApplyOperation.fire(session, self)
        session.selection_mode = modes.SELECT_MODE
        session.selection = self.new_selection

    def undo(self):
        """Undo operation."""
        inv = self.inverse()
        inv.do()
