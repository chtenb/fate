"""A simple clipboard system that can store the content of a single selection."""
# TODO: move clipboard into the core, make it stackbased and turn copy/paste into actions.
from ..session import Session
from ..operation import Operation

Session.clipboard = []

def copy(self):
    self.clipboard = self.content(self.selection)
Session.copy = copy

def paste(self, before=False):
    if self.clipboard:
        content = self.content(self.selection)
        new_content = []
        l = len(self.clipboard)
        for i, interval in enumerate(self.selection):
            if before:
                new_content.append(self.clipboard[i % l] + content[i])
            else:
                new_content.append(content[i] + self.clipboard[i % l])

        operation = Operation(self.selection)
        operation.new_content = new_content
        self.apply(operation)
Session.paste = paste

import logging
logging.info('clipboard system loaded')
