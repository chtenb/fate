"""
Module containing insertmode implementations.
"""
import re
from . import commands
from .operation import Operation
from .operators import Append, Insert
from .selection import Interval
from .commandtools import Compose
from . import selecting # Dependency
from .selecting.selectpattern import selectfullline
from .commands import (emptybefore, emptyafter, selectpreviousfullline, selectindent,
                       selectnextfullline, selectnextchar, selectpreviouschar)
from .clipboard import copy, clear, paste_before, cut
from .mode import Mode
from . import document
from .document import Document
from abc import abstractmethod
from logging import debug
from copy import deepcopy


class InsertMode(Mode):

    """Abstract class for operations dealing with insertion of text."""

    def __init__(self, doc):
        Mode.__init__(self, doc)
        self.allowedcommands.extend([document.next_document, document.previous_document])

    def start(self, doc, *args, **kwargs):
        self.preview_operation = None
        Mode.start(self, doc, *args, **kwargs)
        self.update_operation(doc)

    def processinput(self, doc, userinput):
        if not Mode.processinput(self, doc, userinput):
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
        """Compute and return operation based on insertions and deletions."""
        pass

    @abstractmethod
    def insert(self, doc, string):
        """
        Insert a string (typically a char) in the operation.
        """
        pass


def get_indent(doc, pos):
    """Get the indentation of the line containing position pos."""
    line = selectfullline(doc, interval=Interval(pos, pos))
    string = line.content(doc)
    match = re.search(r'^[ \t]*', string)
    assert match.start() == 0
    return string[match.start(): match.end()]


class ChangeInPlace(InsertMode):

    """
    Make incremental changes to the selected text.
    """

    def __init__(self, doc):
        InsertMode.__init__(self, doc)

    def start(self, doc, *args, **kwargs):
        self.newcontent = ['' for _ in doc.selection]
        self.oldselection = deepcopy(doc.selection)
        InsertMode.start(self, doc, *args, **kwargs)

    def insert(self, doc, string):
        for i in range(len(self.oldselection)):
            if string == '\b':
                # TODO remove multiple whitespaces if possible and doc.expandtab is True
                if self.newcontent[i]:
                    # Remove one char
                    self.newcontent[i] = self.newcontent[i][:-1]
                else:
                    # Extend selection, automatically removing a character, since
                    # newcontent[i] is empty
                    beg, end = self.oldselection[i]
                    self.oldselection[i] = Interval(max(0, beg - 1), end)
            elif string == 'del':
                # Extend selection, automatically removing a character, since
                # the new character is not in newcontent[i]
                beg, end = self.oldselection[i]
                self.oldselection[i] = Interval(beg, min(len(doc.text), end + 1))
            elif string == '\n' and doc.autoindent:
                # Add indent after \n
                newselection = self.preview_operation.compute_newselection()
                cursor_pos = newselection[i][1]
                indent = get_indent(doc, cursor_pos)
                self.newcontent[i] += string + indent
            elif string == '\t' and doc.expandtab:
                # Increase indent
                self.newcontent[i] += ' ' * doc.tabwidth
            else:
                # Add string
                self.newcontent[i] += str(string)

    def compute_operation(self, doc):
        """
        It can happen that this operation is repeated in a situation
        with a larger number of intervals.
        Therefore we take indices modulo the length of the lists l = len(self.insertions)
        newcontent = [doc.selection.content(doc)[i % l][:-self.deletions[i % l] or None]
                       + self.insertions[i % l] for i in range(len(doc.selection))]
        """
        return Operation(doc, self.newcontent[:], deepcopy(self.oldselection))

def init_changeinplace(doc):
    doc.modes.changeinplace = ChangeInPlace(doc)
Document.OnModeInit.add(init_changeinplace)

def get_changeinplace(doc):
    return doc.modes.changeinplace

def start_changeinplace(doc):
    doc.modes.changeinplace.start(doc)
commands.start_changeinplace = start_changeinplace


# TODO: get_changeinplace not working
changebefore = Compose(emptybefore, get_changeinplace, name='ChangeBefore')
commands.changebefore = changebefore

changeafter = Compose(emptyafter, get_changeinplace, name='ChangeAfter')
commands.changeafter = changeafter


class ChangeAround(InsertMode):

    """
    Interactive Operation which deletes `deletions`
    and adds `insertions` around each interval.
    """

    def __init__(self, doc):
        InsertMode.__init__(self, doc)

    def start(self, doc, *args, **kwargs):
        # Insertions before and after can differ because of autoindentation
        self.insertions_before = [''] * len(doc.selection)
        self.insertions_after = [''] * len(doc.selection)
        self.deletions = [0] * len(doc.selection)
        InsertMode.start(self, doc, *args, **kwargs)

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


def init_changearound(doc):
    doc.modes.changearound = ChangeAround(doc)
Document.OnModeInit.add(init_changearound)

def get_changearound(doc):
    return doc.modes.changearound

def start_changearound(doc):
    doc.modes.changearound.start(doc)
commands.start_changearound = start_changearound


openlineafter = Compose(commands.selectfullline, selectindent, copy,
                        selectnextfullline, Append('\n'), selectpreviouschar, emptybefore,
                        paste_before, clear, get_changeinplace, name='openlineafter',
                        docs='Open a line after interval')
commands.openlineafter = openlineafter

openlinebefore = Compose(commands.selectfullline, selectindent, copy,
                         selectnextfullline, Insert('\n'), selectnextchar, emptybefore,
                         paste_before, clear, get_changeinplace, name='openlinebefore',
                         docs='Open a line before interval')
commands.openlinebefore = openlinebefore

cutchange = Compose(cut, get_changeinplace,
                    name='cutchange', docs='Copy and change selected text.')
commands.cutchange = cutchange

