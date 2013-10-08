from ..session import Session
from ..operation import Operation

Session.clipboard = []

def copy(self):
    self.clipboard = self.content(self.selection)
Session.copy = copy

def paste(self):
    operation = Operation(self, self.selection, self.clipboard)
    self.apply(operation)
Session.paste = paste

import logging
logging.info('clipboard system loaded')
