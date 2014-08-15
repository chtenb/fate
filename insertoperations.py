import re
from . import modes
from . import commands
from .operation import Operation
from .operators import Append, Insert
from .selection import Selection, Interval
from .repeat import repeatable
from .commandtools import Compose
from .selectors import (EmptyBefore, PreviousFullLine,
                        SelectIndent, NextFullLine, NextChar, PreviousChar)
from .clipboard import copy, clear, paste_before, Cut
from . import modes

modes.INSERT = 'INSERT'
modes.APPEND = 'APPEND'
modes.SURROUND = 'SURROUND'


class InsertOperation:

    """Abstract class for operations dealing with insertion of text."""

    mode = modes.INSERT

    def __init__(self, document):
        document.mode = self.mode

        # Then keep updating it according to the users changes
        while 1:
            # Execute the operation (excludes adding it to the undotree)
            self.preview_operation = self.compute_operation(document)
            self.preview_operation.do(document)

            document.ui.touch()
            key = document.getkey()

            if key == 'Esc':
                self.preview_operation.undo(document)
                document.mode = modes.SELECT
                break

            self.insert(document, key)

            self.preview_operation.undo(document)

        self.preview_operation(document)

    def compute_operation(self, document):
        """Compute operation based on insertions and deletions."""
        raise NotImplementedError('An abstract method is not callable.')

    def insert(self, document, string):
        """
        Insert a string (typically a char) in the operation.
        """
        raise NotImplementedError('An abstract method is not callable.')


def get_indent(document, pos):
    """Get the indentation of the line containing position pos."""
    line = NextFullLine(document, selection=Selection(intervals=Interval(pos, pos)))
    string = line.content(document)[0]
    match = re.search(r'^[ \t]*', string)
    #debug('pos: ' + str(pos))
    #debug('line: ' + string)
    #debug('match: ' + str((match.start(), match.end())))
    assert match.start() == 0
    return string[match.start(): match.end()]


@repeatable
class ChangeBefore(InsertOperation):

    """
    Interactive Operation which deletes `deletions`
    and adds `insertions` at the head of each interval.
    """

    mode = modes.INSERT

    def __init__(self, document):
        self.insertions = [''] * len(document.selection)
        self.deletions = [0] * len(document.selection)

        InsertOperation.__init__(self, document)

    def insert(self, document, string):
        for i in range(len(document.selection)):
            if string == '\b':
                # TODO remove multiple whitespaces if possible
                # Remove one char
                if self.insertions[i]:
                    self.insertions[i] = self.insertions[i][:-1]
                else:
                    self.deletions[i] += 1
            elif string == '\n' and document.autoindent:
                # Add indent after \n
                new_selection = self.preview_operation.compute_new_selection()
                cursor_pos = new_selection[i][0] + len(self.insertions[i])
                indent = get_indent(document, cursor_pos)
                self.insertions[i] += string + indent
            elif string == '\t' and document.expandtab:
                self.insertions[i] += ' ' * document.tabwidth
            else:
                # Add string
                self.insertions[i] += str(string)

    def compute_operation(self, document):
        # It can happen that this operation is repeated in a situation
        # with a larger number of intervals.
        # Therefore we take indices modulo the length of the lists
        l = len(self.insertions)
        new_content = [self.insertions[i % l]
                       + document.selection.content(document)[i % l][self.deletions[i % l]:]
                       for i in range(len(document.selection))]
        return Operation(document, new_content)

commands.ChangeBefore = ChangeBefore


class ChangeAfter(InsertOperation):

    """
    Interactive Operation which deletes `deletions`
    and adds `insertions` at the head of each interval.
    """

    mode = modes.APPEND

    def __init__(self, document):
        self.insertions = [''] * len(document.selection)
        self.deletions = [0] * len(document.selection)

        InsertOperation.__init__(self, document)

    def insert(self, document, string):
        for i in range(len(document.selection)):
            if string == '\b':
                # TODO remove multiple whitespaces if possible
                # remove one char
                if self.insertions[i]:
                    self.insertions[i] = self.insertions[i][:-1]
                else:
                    self.deletions[i] += 1
            elif string == '\n' and document.autoindent:
                # add indent after \n
                new_selection = self.preview_operation.compute_new_selection()
                cursor_pos = new_selection[i][1]
                indent = get_indent(document, cursor_pos)
                self.insertions[i] += string + indent
            elif string == '\t' and document.expandtab:
                self.insertions[i] += ' ' * document.tabwidth
            else:
                # add string
                self.insertions[i] += str(string)

    def compute_operation(self, document):
        # It can happen that this operation is repeated in a situation
        # with a larger number of intervals.
        # Therefore we take indices modulo the length of the lists
        l = len(self.insertions)
        new_content = [document.selection.content(document)[i % l][:-self.deletions[i % l] or None]
                       + self.insertions[i % l]
                       for i in range(len(document.selection))]
        return Operation(document, new_content)

commands.ChangeAfter = repeatable(ChangeAfter)


@repeatable
class ChangeInPlace(ChangeAfter):

    """
    Interactive Operation which adds `insertions` in place of each interval.
    """

    def compute_operation(self, document):
        # It can happen that this operation is repeated in a situation
        # with a larger number of intervals.
        # Therefore we take indices modulo the length of the lists
        l = len(self.insertions)
        new_content = [self.insertions[i % l] for i in range(len(document.selection))]
        return Operation(document, new_content)

commands.ChangeInPlace = ChangeInPlace


@repeatable
class ChangeAround(InsertOperation):

    """
    Interactive Operation which deletes `deletions`
    and adds `insertions` at the head of each interval.
    """

    mode = modes.SURROUND

    def __init__(self, document):
        # Insertions before and after can differ because of autoindentation
        self.insertions_before = [''] * len(document.selection)
        self.insertions_after = [''] * len(document.selection)
        self.deletions = [0] * len(document.selection)

        InsertOperation.__init__(self, document)

    def insert(self, document, string):
        for i in range(len(document.selection)):
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
            elif string == '\n' and document.autoindent:
                # add indent after \n
                new_selection = self.preview_operation.compute_new_selection()
                cursor_pos_before = new_selection[i][0]
                cursor_pos_after = new_selection[i][1]
                indent_before = get_indent(document, cursor_pos_before)
                indent_after = get_indent(document, cursor_pos_after)
                self.insertions_before[i] += indent_before + string
                self.insertions_after[i] += string + indent_after
            elif string == '\t' and document.expandtab:
                self.insertions_before[i] += ' ' * document.tabwidth
                self.insertions_after[i] += ' ' * document.tabwidth
            else:
                # add string
                self.insertions_before[i] += str(string)
                self.insertions_after[i] += str(string)

    def compute_operation(self, document):
        # It can happen that this operation is repeated in a situation
        # with a larger number of intervals.
        # Therefore we take indices modulo the length of the lists
        l = len(self.insertions_after)
        character_pairs = [('{', '}'), ('[', ']'), ('(', ')'), ('<', '>')]
        new_content = []
        for i in range(len(document.selection)):
            first_string = self.insertions_before[i % l][::-1]
            second_string = self.insertions_after[i % l]
            for first, second in character_pairs:
                first_string = first_string.replace(second, first)
                second_string = second_string.replace(first, second)

            beg, end = self.deletions[i % l], -self.deletions[i % l] or None
            new_content.append(first_string
                               + document.selection.content(document)[i % l][beg:end]
                               + second_string)
        return Operation(document, new_content)

commands.ChangeAround = ChangeAround


OpenLineAfter = Compose(modes.select_mode, PreviousFullLine, SelectIndent, copy,
                        NextFullLine, Append('\n'), PreviousChar, EmptyBefore,
                        paste_before, clear, ChangeAfter, name='OpenLineAfter',
                        docs='Open a line after interval')
commands.OpenLineAfter = repeatable(OpenLineAfter)

OpenLineBefore = Compose(modes.select_mode, NextFullLine, SelectIndent, copy,
                         NextFullLine, Insert('\n'), NextChar, EmptyBefore,
                         paste_before, clear, ChangeAfter, name='OpenLineBefore',
                         docs='Open a line before interval')
commands.OpenLineBefore = repeatable(OpenLineBefore)

CutChange = Compose(Cut, ChangeInPlace,
                    name='CutChange', docs='Copy and change selected text.')
commands.CutChange = repeatable(CutChange)
