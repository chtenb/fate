from . import modes
from . import actions
from .operation import Operation
import re
from .selectors import NextFullLine
from .selection import Selection, Interval

from logging import debug

modes.INSERT = 'INSERT'
modes.APPEND = 'APPEND'
modes.SURROUND = 'SURROUND'


class InsertOperation:

    """Abstract class for operations dealing with insertion of text."""

    def __init__(self, session, selection):
        selection = selection or session.selection
        self.operation = Operation(session, selection=selection)
        self.mode = modes.INSERT

    def __call__(self, session):
        """Execute action."""
        # Execute the operation (includes adding it to the undotree)
        self.operation(session)
        session.mode = self.mode
        # Then keep updating it according to the users changes
        while 1:
            session.ui.touch()
            char = session.ui.getchar()
            if char == 'Esc':
                session.mode = modes.SELECT
                break
            self.new_selection = self.operation.compute_new_selection()
            self.insert(session, char)
            # Make the changes to the session
            self.operation.undo(session)
            self.operation.new_content = self.new_content
            self.operation.do(session)

    @property
    def new_content(self):
        raise NotImplementedError("An abstract method is not callable.")

    def insert(self, session, string):
        """
        Insert a string (typically a char) in the operation.
        By only autoindenting on a single \n, we potentially allow proper pasting.
        """
        raise NotImplementedError("An abstract method is not callable.")


def get_indent(session, pos):
    """Get the indentation of the line containing position pos."""
    line = NextFullLine(session, selection=Selection(intervals=Interval(pos, pos)))
    string = line.content(session)[0]
    match = re.search(r'^[ \t]*', string)
    debug('pos: ' + str(pos))
    debug('line: ' + string)
    debug('match: ' + str((match.start(), match.end())))
    assert match.start() == 0
    return string[match.start(): match.end()]


class ChangeBefore(InsertOperation):
    """
    Interactive Operation which deletes `deletions`
    and adds `insertions` at the head of each interval.
    """
    def __init__(self, session, selection=None):
        InsertOperation.__init__(self, session, selection)
        self.insertions = [''] * len(self.operation.old_selection)
        self.deletions = [0] * len(self.operation.old_selection)
        self.mode = modes.INSERT

    def insert(self, session, string):
        for i in range(len(self.new_selection)):
            if string == '\b':
                # TODO remove multiple whitespaces if possible
                # Remove one char
                if self.insertions[i]:
                    self.insertions[i] = self.insertions[i][:-1]
                else:
                    self.deletions[i] += 1
            elif string == '\n':
                # Add indent after \n
                cursor_pos = self.new_selection[i][0] + len(self.insertions[i])
                indent = get_indent(session, cursor_pos)
                self.insertions[i] += string + indent
            elif string == '\t' and session.expandtab:
                self.insertions[i] += ' ' * session.tabwidth
            else:
                # Add string
                self.insertions[i] += str(string)

    @property
    def new_content(self):
        return [self.insertions[i]
                + self.operation.old_content[i][self.deletions[i]:]
                for i in range(len(self.operation.old_content))]
actions.ChangeBefore = ChangeBefore

class ChangeAfter(InsertOperation):
    """
    Interactive Operation which deletes `deletions`
    and adds `insertions` at the head of each interval.
    """
    def __init__(self, session, selection=None):
        InsertOperation.__init__(self, session, selection)
        self.insertions = [''] * len(self.operation.old_selection)
        self.deletions = [0] * len(self.operation.old_selection)
        self.mode = modes.APPEND

    def insert(self, session, string):
        for i in range(len(self.new_selection)):
            if string == '\b':
                # TODO remove multiple whitespaces if possible
                # remove one char
                if self.insertions[i]:
                    self.insertions[i] = self.insertions[i][:-1]
                else:
                    self.deletions[i] += 1
            elif string == '\n':
                # add indent after \n
                cursor_pos = self.new_selection[i][1]
                indent = get_indent(session, cursor_pos)
                self.insertions[i] += string + indent
            elif string == '\t' and session.expandtab:
                self.insertions[i] += ' ' * session.tabwidth
            else:
                # add string
                self.insertions[i] += str(string)

    @property
    def new_content(self):
        return [self.operation.old_content[i][:-self.deletions[i] or None]
                + self.insertions[i]
                for i in range(len(self.operation.old_content))]
actions.ChangeAfter = ChangeAfter

class ChangeInPlace(ChangeAfter):
    """
    Interactive Operation which adds `insertions` in place of each interval.
    """
    @property
    def new_content(self):
        return [self.insertions[i] for i in range(len(self.operation.old_content))]
actions.ChangeInPlace = ChangeInPlace


class ChangeAround(InsertOperation):

    """
    Interactive Operation which deletes `deletions`
    and adds `insertions` at the head of each interval.
    """
    def __init__(self, session, selection=None):
        InsertOperation.__init__(self, session, selection)
        # Insertions before and after can change because of autoindentation
        self.insertions_before = [''] * len(self.operation.old_selection)
        self.insertions_after = [''] * len(self.operation.old_selection)
        self.deletions = [0] * len(self.operation.old_selection)
        self.mode = modes.SURROUND

    def insert(self, session, string):
        for i in range(len(self.new_selection)):
            if string == '\b':
                # TODO remove multiple whitespaces if possible
                # remove one char
                if self.insertions_before[i] or self.insertions_after[i]:
                    if self.insertions_before[i]:
                        self.insertions_before[i] = self.insertions_before[i][:-1]
                    if self.insertions_after[i]:
                        self.insertions_after[i] = self.insertions_after[i][:-1]
                else:
                    self.deletions[i] += 1
            elif string == '\n':
                # add indent after \n
                cursor_pos_before = self.new_selection[i][0]
                cursor_pos_after = self.new_selection[i][1]
                indent_before = get_indent(session, cursor_pos_before)
                indent_after = get_indent(session, cursor_pos_after)
                self.insertions_before[i] += indent_before + string
                self.insertions_after[i] += string + indent_after
            elif string == '\t' and session.expandtab:
                self.insertions_before[i] += ' ' * session.tabwidth
                self.insertions_after[i] += ' ' * session.tabwidth
            else:
                # add string
                self.insertions_before[i] += str(string)
                self.insertions_after[i] += str(string)

    @property
    def new_content(self):
        character_pairs = [('{', '}'), ('[', ']'), ('(', ')'), ('<', '>')]
        result = []
        for i in range(len(self.operation.old_content)):
            first_string = self.insertions_before[i][::-1]
            second_string = self.insertions_after[i]
            for first, second in character_pairs:
                first_string = first_string.replace(second, first)
                second_string = second_string.replace(first, second)

            beg, end = self.deletions[i], -self.deletions[i] or None
            result.append(first_string
                    + self.operation.old_content[i][beg:end]
                    + second_string)
        return result
actions.ChangeAround = ChangeAround
