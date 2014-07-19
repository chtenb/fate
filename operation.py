"""This module defines the class Operation."""
from . import modes
from .actiontools import Undoable
from .selection import Selection, Interval
from .selectors import SelectIndent


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
        self.new_selection = None # Maybe this can be done neater now
        try:
            self.new_content = new_content or self.old_content[:]
        except AttributeError:
            # new_content has been overriden
            # TODO neater fix for this
            pass

    def __str__(self):
        attributes = [('old_selection', self.old_selection),
                      ('computed new_selection', self.compute_new_selection),
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

    def undo(self, session):
        """Undo operation."""
        self._apply(session, inverse=True)

    def _apply(self, session, inverse=False):
        """Apply self to the session."""
        if inverse:
            if self.new_selection == None:
                raise Exception(
                    'An operation that has not been applied cannot be undone.'
                )
            old_selection = self.new_selection
            new_selection = self.old_selection
            new_content = self.old_content
        else:
            self.new_selection = self.compute_new_selection()
            new_selection = self.new_selection
            old_selection = self.old_selection
            new_content = self.new_content

        #print(self)
        #print(session.text)
        #print(session.selection)

        # Make sure the application of this operation is valid at this moment
        assert session.selection == old_selection

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
        session.selection_mode = modes.SELECT_MODE
        session.selection = new_selection


class InsertOperation:

    """Abstract class for operations dealing with insertion of text."""

    def __init__(self, session, selection=None):
        selection = selection or session.selection
        self.operation = Operation(session, selection)
        self.insertions = [''] * len(selection)
        self.deletions = [0] * len(selection)

    def __call__(self, session):
        """Execute action."""
        # Execute the operation
        self.operation(session)
        # Then keep updating it according to the users changes
        while 1:
            session.ui.touch()
            char = session.ui.getchar()
            if char == 'Esc':
                break
            self.insert(session, char)

    @property
    def new_content(self, session):
        raise NotImplementedError("An abstract method is not callable.")

    def insert(self, session, string):
        """
        Insert a string (typically a char) in the operation.
        By only autoindenting on a single \n, we potentially allow proper pasting.
        """
        self.operation.new_selection = self.operation.compute_new_selection()

        # Very ugly way to get a indent string for each interval in the selection
        indent = [SelectIndent(session, Selection([interval])).content(session)[0]
                for interval in self.operation.new_selection]

        assert (len(self.operation.new_selection)
                == len(indent)
                == len(self.insertions)
                == len(self.deletions))

        for i in range(len(self.operation.new_selection)):
            if string == '\b':
                # TODO remove multiple whitespaces if possible
                # remove one char
                if self.insertions[i]:
                    self.insertions[i] = self.insertions[i][:-1]
                else:
                    self.deletions[i] += 1
            elif string == '\n':
                # add indent after \n
                self.insertions[i] += string + indent[i]
            elif string == '\t' and session.expandtab:
                self.insertions[i] += ' ' * session.tabwidth
            else:
                # add string
                self.insertions[i] += str(string)

        # Make the changes to the session
        self.operation.undo(session)
        self.operation.new_content = self.new_content
        self.operation.do(session)
