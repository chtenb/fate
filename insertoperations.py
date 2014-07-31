from . import modes
from . import actions
from .operation import Operation
import re
from .selectors import NextFullLine
from .selection import Selection, Interval
from .repeat import start_recording, stop_recording

from logging import debug

modes.INSERT = 'INSERT'
modes.APPEND = 'APPEND'
modes.SURROUND = 'SURROUND'


class InsertOperation:

    """Abstract class for operations dealing with insertion of text."""

    mode = modes.INSERT

    def __init__(self, session):
        session.mode = self.mode

        self.record(session)
        start_recording(session)

        # Then keep updating it according to the users changes
        while 1:
            # Execute the operation (excludes adding it to the undotree)
            self.preview_operation = self.compute_operation(session)
            self.preview_operation.do(session)

            session.ui.touch()
            char = session.getchar()

            if char == 'Esc':
                self.preview_operation.undo(session)
                session.mode = modes.SELECT
                break

            self.insert(session, char)

            self.preview_operation.undo(session)

        self.preview_operation(session)

        stop_recording(session)

    @classmethod
    def record(cls, session):
        session.current_repeatable_action = cls

    def compute_operation(self, session):
        """Compute operation based on insertions and deletions."""
        raise NotImplementedError('An abstract method is not callable.')

    def insert(self, session, string):
        """
        Insert a string (typically a char) in the operation.
        """
        raise NotImplementedError('An abstract method is not callable.')


def get_indent(session, pos):
    """Get the indentation of the line containing position pos."""
    line = NextFullLine(session, selection=Selection(intervals=Interval(pos, pos)))
    string = line.content(session)[0]
    match = re.search(r'^[ \t]*', string)
    #debug('pos: ' + str(pos))
    #debug('line: ' + string)
    #debug('match: ' + str((match.start(), match.end())))
    assert match.start() == 0
    return string[match.start(): match.end()]


class ChangeBefore(InsertOperation):

    """
    Interactive Operation which deletes `deletions`
    and adds `insertions` at the head of each interval.
    """

    mode = modes.INSERT

    def __init__(self, session):
        self.insertions = [''] * len(session.selection)
        self.deletions = [0] * len(session.selection)

        InsertOperation.__init__(self, session)

    def insert(self, session, string):
        for i in range(len(session.selection)):
            if string == '\b':
                # TODO remove multiple whitespaces if possible
                # Remove one char
                if self.insertions[i]:
                    self.insertions[i] = self.insertions[i][:-1]
                else:
                    self.deletions[i] += 1
            elif string == '\n' and session.autoindent:
                # Add indent after \n
                new_selection = self.preview_operation.compute_new_selection()
                cursor_pos = new_selection[i][0] + len(self.insertions[i])
                indent = get_indent(session, cursor_pos)
                self.insertions[i] += string + indent
            elif string == '\t' and session.expandtab:
                self.insertions[i] += ' ' * session.tabwidth
            else:
                # Add string
                self.insertions[i] += str(string)

    def compute_operation(self, session):
        # It can happen that this operation is repeated in a situation
        # with a larger number of intervals.
        # Therefore we take indices modulo the length of the lists
        l = len(self.insertions)
        new_content = [self.insertions[i % l]
                       + session.selection.content(session)[i % l][self.deletions[i % l]:]
                       for i in range(len(session.selection))]
        return Operation(session, new_content)

actions.ChangeBefore = ChangeBefore


class ChangeAfter(InsertOperation):

    """
    Interactive Operation which deletes `deletions`
    and adds `insertions` at the head of each interval.
    """

    mode = modes.APPEND

    def __init__(self, session):
        self.insertions = [''] * len(session.selection)
        self.deletions = [0] * len(session.selection)

        InsertOperation.__init__(self, session)

    def insert(self, session, string):
        for i in range(len(session.selection)):
            if string == '\b':
                # TODO remove multiple whitespaces if possible
                # remove one char
                if self.insertions[i]:
                    self.insertions[i] = self.insertions[i][:-1]
                else:
                    self.deletions[i] += 1
            elif string == '\n' and session.autoindent:
                # add indent after \n
                new_selection = self.preview_operation.compute_new_selection()
                cursor_pos = new_selection[i][1]
                indent = get_indent(session, cursor_pos)
                self.insertions[i] += string + indent
            elif string == '\t' and session.expandtab:
                self.insertions[i] += ' ' * session.tabwidth
            else:
                # add string
                self.insertions[i] += str(string)

    def compute_operation(self, session):
        # It can happen that this operation is repeated in a situation
        # with a larger number of intervals.
        # Therefore we take indices modulo the length of the lists
        l = len(self.insertions)
        new_content = [session.selection.content(session)[i % l][:-self.deletions[i % l] or None]
                       + self.insertions[i % l]
                       for i in range(len(session.selection))]
        return Operation(session, new_content)

actions.ChangeAfter = ChangeAfter


class ChangeInPlace(ChangeAfter):

    """
    Interactive Operation which adds `insertions` in place of each interval.
    """

    def compute_operation(self, session):
        # It can happen that this operation is repeated in a situation
        # with a larger number of intervals.
        # Therefore we take indices modulo the length of the lists
        l = len(self.insertions)
        new_content = [self.insertions[i % l] for i in range(len(session.selection))]
        return Operation(session, new_content)

actions.ChangeInPlace = ChangeInPlace


class ChangeAround(InsertOperation):

    """
    Interactive Operation which deletes `deletions`
    and adds `insertions` at the head of each interval.
    """

    mode = modes.SURROUND

    def __init__(self, session):
        # Insertions before and after can differ because of autoindentation
        self.insertions_before = [''] * len(session.selection)
        self.insertions_after = [''] * len(session.selection)
        self.deletions = [0] * len(session.selection)

        InsertOperation.__init__(self, session)

    def insert(self, session, string):
        for i in range(len(session.selection)):
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
            elif string == '\n' and session.autoindent:
                # add indent after \n
                new_selection = self.preview_operation.compute_new_selection()
                cursor_pos_before = new_selection[i][0]
                cursor_pos_after = new_selection[i][1]
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

    def compute_operation(self, session):
        # It can happen that this operation is repeated in a situation
        # with a larger number of intervals.
        # Therefore we take indices modulo the length of the lists
        l = len(self.insertions_after)
        character_pairs = [('{', '}'), ('[', ']'), ('(', ')'), ('<', '>')]
        new_content = []
        for i in range(len(session.selection)):
            first_string = self.insertions_before[i % l][::-1]
            second_string = self.insertions_after[i % l]
            for first, second in character_pairs:
                first_string = first_string.replace(second, first)
                second_string = second_string.replace(first, second)

            beg, end = self.deletions[i % l], -self.deletions[i % l] or None
            new_content.append(first_string
                               + session.selection.content(session)[i % l][beg:end]
                               + second_string)
        return Operation(session, new_content)

actions.ChangeAround = ChangeAround
