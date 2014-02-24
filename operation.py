"""This module defines the class Operation."""
from .selection import Selection
from .action import Action
from .selectors import select_indent
from . import modes
from copy import copy, deepcopy
import logging


class Operation(Action):
    """
    A container of modified content of a selection.
    Can be inverted such that the operation can be undone by applying the inverse.
    The members are `old_selection`, `old_content`, `new_content` and `new_selection`.
    """
    def __init__(self, selection, new_content=None):
        Action.__init__(self, selection.session)
        self.old_selection = selection
        self.old_content = selection.content
        try:
            self.new_content = new_content or self.old_content[:]
        except AttributeError:
            # new_content has been overriden
            # TODO neater fix for this
            pass

    def __str__(self):
        attributes = [('old_selection', self.old_selection),
                      ('new_selection', self.new_selection),
                      ('old_content', self.old_content),
                      ('new_content', self.new_content)]
        return '\n'.join([k + ': ' + str(v) for k, v in attributes])

    def __deepcopy__(self, memo):
        result = copy(self)
        result.old_selection = deepcopy(self.old_selection, memo)
        result.old_content = self.old_content[:]
        try:
            self.new_content = self.new_content[:]
        except AttributeError:
            # new_content has been overriden
            # TODO neater fix for this
            pass
        return result

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

    def _do(self, inverse=False):
        """Apply self to the session."""
        if inverse:
            old_selection = self.new_selection
            new_selection = self.old_selection
            new_content = self.old_content
        else:
            new_selection = self.new_selection
            old_selection = self.old_selection
            new_content = self.new_content

        session = self.session
        partition = old_selection.partition()
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
        session.text_changed = True
        session.selection_mode = modes.SELECT_MODE
        session.selection = new_selection

    def _undo(self):
        """Undo operation."""
        self._do(inverse=True)


class InsertOperation(Operation):
    """An operation for the change_before operator."""
    def __init__(self, session):
        selection = session.selection
        Operation.__init__(self, selection)
        self.insertions = ['' for _ in selection]
        self.deletions = [0 for _ in selection]
        self.feed('')

    def __str__(self):
        return ('insertions: ' + str(self.insertions) + '\n'
                + 'deletions: ' + str(self.deletions) + '\n'
                + Operation.__str__(self))

    def __deepcopy__(self, memo):
        result = Operation.__deepcopy__(self, memo)
        result.insertions = self.insertions[:]
        result.deletions = self.deletions[:]
        return result

    def feed(self, string):
        """Feed a string (typically a char) to the operation."""
        for i in range(len(self.new_selection)):
            for char in string:
                if char == '\b':
                    # remove char
                    if self.insertions[i]:
                        self.insertions[i] = self.insertions[i][:-1]
                    else:
                        self.deletions[i] += 1
                elif char == '\n':
                    # get indent
                    indent = select_indent(self.session, preview=True, selection=Selection(self.session, intervals=[self.new_selection[i]]))
                    indent = indent.content[0]
                    # add indent after \n
                    self.insertions[i] += char + indent
                else:
                    # add char
                    self.insertions[i] += char

        # Undo the previous version of self
        self.session.actiontree.hard_undo()
        # And apply the current version of self
        self.do()

    def done(self):
        """Finish constructing this operation."""
        self.session.insertoperation = None

