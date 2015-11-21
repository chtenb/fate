from . import selecting # Dependency
from abc import abstractmethod
from logging import debug
from copy import deepcopy

from .insertoperations import InsertMode, get_indent
from .operation import Operation

class Completable(InsertMode):

    """
    InsertMode which also provides autocompletions.
    Restricted to a single interval.
    """

    def __init__(self, doc, callback=None):
        InsertMode.__init__(self, doc, callback)
        self.allowedcommands.extend([self.next_completion, self.next_completion_or_tab,
                                     self.previous_completion])

        self.keymap.update({
            '\t': self.next_completion_or_tab,
            'Btab': self.previous_completion
        })

        # Init completions
        self.completions = []
        self.selected_completion = 0

    @abstractmethod
    def cursor_position(self, doc):
        pass

    def complete_enabled(self, doc):
        return len(doc.selection) == 1 and doc.completer != None

    def next_completion(self, doc):
        if self.complete_enabled(doc) and self.completions:
            self.selected_completion = (
                self.selected_completion + 1) % len(self.completions)
            self.insert_completion(doc)

    def previous_completion(self, doc):
        if self.complete_enabled(doc) and self.completions:
            self.selected_completion = (
                self.selected_completion - 1) % len(self.completions)
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

        doc.completer.parse_file()
        complete_result = doc.completer.complete()
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


#
# EXAMPLE FOR COMPLETABLE
#
class ExampleCompletable(Completable):

    def __init__(self, doc, callback=None):
        self.newcontent = ['' for _ in doc.selection]
        self.oldselection = deepcopy(doc.selection)
        Completable.__init__(self, doc, callback)
        self.update_operation(doc)

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
        debug('pruned result: {}'.format(
            self.newcontent[0][:self.completion_start_pos - beg]))

        self.newcontent[0] = self.newcontent[0][:self.completion_start_pos - beg]
        #self.deletions[0] = len(self.newcontent[0]) - (self.completion_start_pos - beg)

        self.newcontent[0] += self.completions[self.selected_completion]
        self.update_operation(doc)
