from .selection import Selection
import copy
import logging


class Operation:
    """Container of modified content of a selection"""
    @property
    def new_selection(self):
        beg = self.old_selection[0][0]
        end = beg + len(self.new_content[0])
        result = Selection(self.session, [(beg, end)])
        for i in range(1, len(self.old_selection)):
            beg = end + self.old_selection[i][0] - self.old_selection[i - 1][1]
            end = beg + len(self.new_content[i])
            result.add((beg, end))
        return result

    def __init__(self, selection):
        self.session = selection.session
        self.old_selection = selection
        self.old_content = self.session.content(selection)
        self.new_content = self.old_content[:]

        # new_selection should be computed on apply only
        #
        #beg = selection[0][0]
        #end = beg + len(self.new_content[0])
        #self.new_selection = Selection(session, [(beg, end)])
        #for i in range(1, len(selection)):
        #    beg = end + selection[i][0] - selection[i - 1][1]
        #    end = beg + len(self.new_content[i])
        #    self.new_selection.add((beg, end))

    def inverse(self):
        result = copy.copy(self)
        result.old_selection = self.new_selection
        result.old_content, result.new_content = result.new_content, result.old_content
        return result

