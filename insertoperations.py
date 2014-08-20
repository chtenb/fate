import re
from . import commands
from .operation import Operation
from .operators import Append, Insert, delete
from .selection import Selection, Interval
from .repeat import repeatable
from .commandtools import Compose
from .selectors import (emptybefore, previousfullline, selectindent,
                        nextfullline, nextchar, previouschar)
from .clipboard import copy, clear, paste_before, Cut
from .mode import cancel, Mode
from . import document


class InsertMode(Mode):

    """Abstract class for operations dealing with insertion of text."""

    def __init__(self, doc):
        Mode.__init__(self)
        self.allowedcommands = [document.next_document, document.previous_document]
        doc.mode = self

        # Init trivial starting operation
        self.preview_operation = self.compute_operation(doc)

    def processinput(self, doc, userinput):
        if type(userinput) != str:
            if userinput in self.allowedcommands:
                userinput(doc)
            return

        # If userinput is Cancel, exit the insert mode
        if userinput == 'Cancel':
            self.stop(doc)
            return

        # If userinput is not a character literal, don't insert it literally
        if len(userinput) > 1:
            if userinput in doc.keymap:
                command = doc.keymap[userinput]
                if command in self.allowedcommands:
                    command(doc)
            return

        self.insert(doc, userinput)

        # Update operation
        # TODO: this is gonna be easier if text allows preview operations
        if self.preview_operation != None:
            self.preview_operation.undo(doc)

        # Execute the operation (excludes adding it to the undotree)
        self.preview_operation = self.compute_operation(doc)
        self.preview_operation.do(doc)

    def stop(self, doc):
        if self.preview_operation != None:
            self.preview_operation.undo(doc)
            self.preview_operation(doc)
        doc.mode = None

    def __str__(self):
        return 'INSERT'

    def compute_operation(self, doc):
        """Compute operation based on insertions and deletions."""
        raise NotImplementedError('An abstract method is not callable.')

    def insert(self, doc, string):
        """
        Insert a string (typically a char) in the operation.
        """
        raise NotImplementedError('An abstract method is not callable.')


def get_indent(doc, pos):
    """Get the indentation of the line containing position pos."""
    line = nextfullline(doc, selection=Selection(intervals=Interval(pos, pos)))
    string = line.content(doc)[0]
    match = re.search(r'^[ \t]*', string)
    #debug('pos: ' + str(pos))
    #debug('line: ' + string)
    #debug('match: ' + str((match.start(), match.end())))
    assert match.start() == 0
    return string[match.start(): match.end()]


@repeatable
class ChangeBefore(InsertMode):

    """
    Interactive Operation which deletes `deletions`
    and adds `insertions` at the head of each interval.
    """

    def __init__(self, doc):
        self.insertions = [''] * len(doc.selection)
        self.deletions = [0] * len(doc.selection)

        InsertMode.__init__(self, doc)

    def insert(self, doc, string):
        for i in range(len(doc.selection)):
            if string == '\b':
                # TODO remove multiple whitespaces if possible
                # Remove one char
                if self.insertions[i]:
                    self.insertions[i] = self.insertions[i][:-1]
                else:
                    self.deletions[i] += 1
            elif string == '\n' and doc.autoindent:
                # Add indent after \n
                new_selection = self.preview_operation.compute_new_selection()
                cursor_pos = new_selection[i][0] + len(self.insertions[i])
                indent = get_indent(doc, cursor_pos)
                self.insertions[i] += string + indent
            elif string == '\t' and doc.expandtab:
                self.insertions[i] += ' ' * doc.tabwidth
            else:
                # Add string
                self.insertions[i] += str(string)

    def compute_operation(self, doc):
        # It can happen that this operation is repeated in a situation
        # with a larger number of intervals.
        # Therefore we take indices modulo the length of the lists
        l = len(self.insertions)
        new_content = [self.insertions[i % l]
                       + doc.selection.content(doc)[i % l][self.deletions[i % l]:]
                       for i in range(len(doc.selection))]
        return Operation(doc, new_content)

commands.ChangeBefore = ChangeBefore


class ChangeAfter(InsertMode):

    """
    Interactive Operation which deletes `deletions`
    and adds `insertions` at the head of each interval.
    """

    def __init__(self, doc):
        self.insertions = [''] * len(doc.selection)
        self.deletions = [0] * len(doc.selection)

        InsertMode.__init__(self, doc)

    def __str__(self):
        return 'APPEND'

    def insert(self, doc, string):
        for i in range(len(doc.selection)):
            if string == '\b':
                # TODO remove multiple whitespaces if possible
                # remove one char
                if self.insertions[i]:
                    self.insertions[i] = self.insertions[i][:-1]
                else:
                    self.deletions[i] += 1
            elif string == '\n' and doc.autoindent:
                # add indent after \n
                new_selection = self.preview_operation.compute_new_selection()
                cursor_pos = new_selection[i][1]
                indent = get_indent(doc, cursor_pos)
                self.insertions[i] += string + indent
            elif string == '\t' and doc.expandtab:
                self.insertions[i] += ' ' * doc.tabwidth
            else:
                # add string
                self.insertions[i] += str(string)

    def compute_operation(self, doc):
        # It can happen that this operation is repeated in a situation
        # with a larger number of intervals.
        # Therefore we take indices modulo the length of the lists
        l = len(self.insertions)
        new_content = [doc.selection.content(doc)[i % l][:-self.deletions[i % l] or None]
                       + self.insertions[i % l]
                       for i in range(len(doc.selection))]
        return Operation(doc, new_content)

commands.ChangeAfter = repeatable(ChangeAfter)


# TODO: write ChangeInPlace as composition of delete and ChangeBefore
@repeatable
class ChangeInPlace(ChangeAfter):

    """
    Interactive Operation which adds `insertions` in place of each interval.
    """

    def compute_operation(self, doc):
        # It can happen that this operation is repeated in a situation
        # with a larger number of intervals.
        # Therefore we take indices modulo the length of the lists
        l = len(self.insertions)
        new_content = [self.insertions[i % l] for i in range(len(doc.selection))]
        return Operation(doc, new_content)

commands.ChangeInPlace = ChangeInPlace

commands.ChangeInPlace = Compose(delete, ChangeBefore)


@repeatable
class ChangeAround(InsertMode):

    """
    Interactive Operation which deletes `deletions`
    and adds `insertions` at the head of each interval.
    """

    def __init__(self, doc):
        # Insertions before and after can differ because of autoindentation
        self.insertions_before = [''] * len(doc.selection)
        self.insertions_after = [''] * len(doc.selection)
        self.deletions = [0] * len(doc.selection)

        InsertMode.__init__(self, doc)

    def __str__(self):
        return 'SURROUND'

    def insert(self, doc, string):
        for i in range(len(doc.selection)):
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
            elif string == '\n' and doc.autoindent:
                # add indent after \n
                new_selection = self.preview_operation.compute_new_selection()
                cursor_pos_before = new_selection[i][0]
                cursor_pos_after = new_selection[i][1]
                indent_before = get_indent(doc, cursor_pos_before)
                indent_after = get_indent(doc, cursor_pos_after)
                self.insertions_before[i] += indent_before + string
                self.insertions_after[i] += string + indent_after
            elif string == '\t' and doc.expandtab:
                self.insertions_before[i] += ' ' * doc.tabwidth
                self.insertions_after[i] += ' ' * doc.tabwidth
            else:
                # add string
                self.insertions_before[i] += str(string)
                self.insertions_after[i] += str(string)

    def compute_operation(self, doc):
        # It can happen that this operation is repeated in a situation
        # with a larger number of intervals.
        # Therefore we take indices modulo the length of the lists
        l = len(self.insertions_after)
        character_pairs = [('{', '}'), ('[', ']'), ('(', ')'), ('<', '>')]
        new_content = []
        for i in range(len(doc.selection)):
            first_string = self.insertions_before[i % l][::-1]
            second_string = self.insertions_after[i % l]
            for first, second in character_pairs:
                first_string = first_string.replace(second, first)
                second_string = second_string.replace(first, second)

            beg, end = self.deletions[i % l], -self.deletions[i % l] or None
            new_content.append(first_string
                               + doc.selection.content(doc)[i % l][beg:end]
                               + second_string)
        return Operation(doc, new_content)

commands.ChangeAround = ChangeAround


OpenLineAfter = Compose(cancel, previousfullline, selectindent, copy,
                        nextfullline, Append('\n'), previouschar, emptybefore,
                        paste_before, clear, ChangeAfter, name='OpenLineAfter',
                        docs='Open a line after interval')
commands.OpenLineAfter = repeatable(OpenLineAfter)

OpenLineBefore = Compose(cancel, nextfullline, selectindent, copy,
                         nextfullline, Insert('\n'), nextchar, emptybefore,
                         paste_before, clear, ChangeAfter, name='OpenLineBefore',
                         docs='Open a line before interval')
commands.OpenLineBefore = repeatable(OpenLineBefore)

CutChange = Compose(Cut, ChangeInPlace,
                    name='CutChange', docs='Copy and change selected text.')
commands.CutChange = repeatable(CutChange)
