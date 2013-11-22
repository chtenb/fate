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

        operation = Operation(self, self.selection, new_content)
        self.apply(operation)
Session.paste = paste

import logging
logging.info('clipboard system loaded')
