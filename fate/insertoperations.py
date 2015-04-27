"""
Module containing insertmode implementations.
"""
import re
from . import commands
from .operation import Operation
from .operators import Append, Insert, delete
from .selection import Interval
from .commandtools import Compose
from .selectors import selectfullline as selectfullline
from .commands import (emptybefore, selectpreviousfullline, selectindent,
                       selectnextfullline, selectnextchar, selectpreviouschar)
from .clipboard import copy, clear, paste_before, Cut
from .mode import Mode
from . import document
from . import ycm
from abc import abstractmethod
from logging import error, debug


class InsertMode(Mode):

    """Abstract class for operations dealing with insertion of text."""

    def __init__(self, doc, callback=None):
        Mode.__init__(self, doc, callback)
        self.allowedcommands.extend([document.next_document, document.previous_document])

        # Init trivial starting operation
        self.preview_operation = self.compute_operation(doc)
        self.start(doc)

        # Init completions
        self.completions = []
        self.selected_completion = 0

        self.keymap = {
            'Cancel': self.stop,
        }

    def processinput(self, doc, userinput):
        if type(userinput) != str:
            if userinput in self.allowedcommands:
                userinput(doc)
            else:
                error('Can\'t process input {}'.format(repr(userinput)))

        # If userinput is in keymap, execute corresponding command
        elif userinput in self.keymap:
            self.keymap[userinput](doc)

        # If userinput is a single character, insert it
        elif len(userinput) == 1:
            self.insert_and_update(doc, userinput)

    def insert_and_update(self, doc, userinput):
        self.insert(doc, userinput)
        self.update_operation(doc)

    def stop(self, doc):
        if self.preview_operation != None:
            self.preview_operation.undo(doc)
            self.preview_operation(doc)
        Mode.stop(self, doc)

    def update_operation(self, doc):
        # TODO: this is gonna be easier if text allows preview operations
        if self.preview_operation != None:
            self.preview_operation.undo(doc)

        # Execute the operation (excludes adding it to the undotree)
        self.preview_operation = self.compute_operation(doc)
        self.preview_operation.do(doc)

    @abstractmethod
    def compute_operation(self, doc):
        """Compute operation based on insertions and deletions."""
        raise NotImplementedError('An abstract method is not callable.')

    @abstractmethod
    def insert(self, doc, string):
        """
        Insert a string (typically a char) in the operation.
        """
        raise NotImplementedError('An abstract method is not callable.')


class Completable(InsertMode):

    """
    InsertMode which also provides autocompletions.
    Restricted to a single interval.
    """

    def __init__(self, doc, callback=None):
        self.newcontent = doc.selection.content(doc)

        InsertMode.__init__(self, doc, callback)
        self.allowedcommands.extend([self.next_completion, self.next_completion_or_tab,
                                     self.previous_completion])

        self.keymap.update({
            '\t': self.next_completion_or_tab,
            'Btab': self.previous_completion
        })

    @abstractmethod
    def cursor_position(self, doc):
        pass

    def complete_enabled(self, doc):
        return len(doc.selection) == 1 and doc.completer != None

    def next_completion(self, doc):
        if self.complete_enabled(doc) and self.completions:
            self.selected_completion = ((self.selected_completion + 1)
                                        % len(self.completions))
            self.insert_completion(doc)

    def previous_completion(self, doc):
        if self.complete_enabled(doc) and self.completions:
            self.selected_completion = ((self.selected_completion - 1)
                                        % len(self.completions))
            self.insert_completion(doc)

    def next_completion_or_tab(self, doc):
        if self.complete_enabled(doc) and len(self.completions) > 1:
            self.next_completion(doc)
        else:
            self.insert_and_update(doc, '\t')

    @abstractmethod
    def insert_completion(self, doc):
        pass

    def update_completions(self, doc):
        assert self.complete_enabled(doc)
        beg = doc.selection[0][0]

        ycm.parse_file(doc)
        complete_result = ycm.complete(doc)
        if complete_result:
            self.completion_start_pos, self.completions = complete_result
            self.completions.insert(0, self.newcontent[0])

        if not complete_result or self.completion_start_pos < beg:
            self.completions = []
            self.completion_start_pos = -1

        self.selected_completion = 0

    def insert_and_update(self, doc, userinput):
        self.insert(doc, userinput)
        self.update_operation(doc)
        if self.complete_enabled(doc):
            self.update_completions(doc)


def get_indent(doc, pos):
    """Get the indentation of the line containing position pos."""
    line = selectfullline(doc, interval=Interval(pos, pos))
    string = line.content(doc)
    match = re.search(r'^[ \t]*', string)
    assert match.start() == 0
    return string[match.start(): match.end()]


class ChangeAfter(Completable):

    """
    """

    def cursor_position(self, doc):
        return doc.selection[0][1]

    def insert(self, doc, string):
        for i in range(len(doc.selection)):
            if string == '\b':
                # TODO remove multiple whitespaces if possible
                # remove one char
                if self.newcontent[i]:
                    self.newcontent[i] = self.newcontent[i][:-1]
            elif string == '\n' and doc.autoindent:
                # add indent after \n
                newselection = self.preview_operation.compute_newselection()
                cursor_pos = newselection[i][1]
                indent = get_indent(doc, cursor_pos)
                self.newcontent[i] += string + indent
            elif string == '\t' and doc.expandtab:
                # increase indent
                self.newcontent[i] += ' ' * doc.tabwidth
            else:
                # add string
                self.newcontent[i] += str(string)

    def compute_operation(self, doc):
        # It can happen that this operation is repeated in a situation
        # with a larger number of intervals.
        # Therefore we take indices modulo the length of the lists
        #l = len(self.insertions)
        # newcontent = [doc.selection.content(doc)[i % l][:-self.deletions[i % l] or None]
                      #+ self.insertions[i % l]
                      # for i in range(len(doc.selection))]
        return Operation(doc, self.newcontent[:])

    def insert_completion(self, doc):
        assert self.complete_enabled(doc)
        beg = doc.selection[0][0]
        assert self.completion_start_pos >= beg
        debug('beg: {}'.format(beg))
        debug('completion start: {}'.format(self.completion_start_pos))
        debug('pruned result: {}'.format(self.newcontent[0][:self.completion_start_pos - beg]))

        self.newcontent[0] = self.newcontent[0][:self.completion_start_pos - beg]
        #self.deletions[0] = len(self.newcontent[0]) - (self.completion_start_pos - beg)

        self.newcontent[0] += self.completions[self.selected_completion]
        self.update_operation(doc)

commands.ChangeAfter = ChangeAfter


class ChangeBefore(InsertMode):

    """
    Interactive Operation which deletes `deletions`
    and adds `insertions` at the head of each interval.
    """

    def __init__(self, doc, callback=None):
        self.insertions = [''] * len(doc.selection)
        self.deletions = [0] * len(doc.selection)

        InsertMode.__init__(self, doc, callback)

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
                newselection = self.preview_operation.compute_newselection()
                cursor_pos = newselection[i][0] + len(self.insertions[i])
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
        newcontent = [self.insertions[i % l]
                      + doc.selection.content(doc)[i % l][self.deletions[i % l]:]
                      for i in range(len(doc.selection))]
        return Operation(doc, newcontent)

    # def cursor_position(self, doc):
        # return doc.selection[0][0] + len(self.insertions[0])

    # def insert_completion(self, doc):
        #assert self.complete_enabled(doc)
        #beg = doc.selection[0][0]
        #assert self.completion_start_pos >= beg
        #...

commands.ChangeBefore = ChangeBefore


ChangeInPlace = Compose(delete, ChangeAfter, name='ChangeInPlace')
commands.ChangeInPlace = ChangeInPlace


class ChangeAround(InsertMode):

    """
    Interactive Operation which deletes `deletions`
    and adds `insertions` around each interval.
    """

    def __init__(self, doc, callback=None):
        # Insertions before and after can differ because of autoindentation
        self.insertions_before = [''] * len(doc.selection)
        self.insertions_after = [''] * len(doc.selection)
        self.deletions = [0] * len(doc.selection)

        InsertMode.__init__(self, doc, callback)

    def cursor_position(self, doc):
        return doc.selection[0][0]

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
                newselection = self.preview_operation.compute_newselection()
                cursor_pos_before = newselection[i][0]
                cursor_pos_after = newselection[i][1]
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
        newcontent = []
        for i in range(len(doc.selection)):
            first_string = self.insertions_before[i % l][::-1]
            second_string = self.insertions_after[i % l]
            for first, second in character_pairs:
                first_string = first_string.replace(second, first)
                second_string = second_string.replace(first, second)

            beg, end = self.deletions[i % l], -self.deletions[i % l] or None
            newcontent.append(first_string
                              + doc.selection.content(doc)[i % l][beg:end]
                              + second_string)
        return Operation(doc, newcontent)

commands.ChangeAround = ChangeAround


OpenLineAfter = Compose(selectpreviousfullline, selectindent, copy,
                        selectnextfullline, Append('\n'), selectpreviouschar, emptybefore,
                        paste_before, clear, ChangeAfter, name='OpenLineAfter',
                        docs='Open a line after interval')
commands.OpenLineAfter = OpenLineAfter

OpenLineBefore = Compose(selectnextfullline, selectindent, copy,
                         selectnextfullline, Insert('\n'), selectnextchar, emptybefore,
                         paste_before, clear, ChangeAfter, name='OpenLineBefore',
                         docs='Open a line before interval')
commands.OpenLineBefore = OpenLineBefore

CutChange = Compose(Cut, ChangeBefore,
                    name='Cut & Change', docs='Copy and change selected text.')
commands.CutChange = CutChange
