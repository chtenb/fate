from importlib import import_module
import subprocess
from logging import info

from ..document import Document
from ..mode import Mode
from .. import commands
from ..selection import Selection
from logging import debug

# Dependencies
from .. import filetype


class ErrorChecker:

    """Container for formatter configuration."""

    def check(self, document):
        """Has to return and errorlist."""
        pass


def init_errorlist(document):
    """
    An errorlist is a list of tuples of the form
    (['error'|'warning'], <interval>, <message>)
    """
    document.errorlist = []
Document.OnDocumentInit.add(init_errorlist)

def checkerrors(doc):
    """If doc has a errorchecker, execute it and make results visible."""
    errorchecker = doc.errorchecker
    if errorchecker:
        errorlist = errorchecker.check(doc)
        doc.errorlist = errorlist
        for etype, interval, _ in errorlist:
            beg, end = interval
            for pos in range(beg, end):
                doc.labeling[pos] = etype
commands.checkerrors = checkerrors


def load_filetype_formatter(doc):
    doc.errorchecker = None
    if doc.filetype:
        try:
            module = import_module(__name__ + '.' + doc.filetype)
        except ImportError:
            info('No errorchecker script found for filetype ' + doc.filetype)
        else:
            info('Errorchecker script found for filetype ' + doc.filetype)
            doc.errorchecker = module.errorchecker

Document.OnFileTypeLoaded.add(load_filetype_formatter)

# TODO: turn up, down into commands?

class ErrorMode(Mode):

    """
    Walk around in error list using j/k.
    """

    def __init__(self, document, callback=None):
        Mode.__init__(self, document, callback)
        self.keymap = {
            'k': self.up,
            'j': self.down,
            '\n': self.jump_to_error,
            'Cancel': self.stop
        }
        self.allowedcommands = [
            commands.next_document, commands.previous_document, commands.quit_document,
            commands.quit_all, commands.open_document, commands.force_quit
        ]

        self.index = 0
        checkerrors(document)
        self.start(document)

    def processinput(self, document, userinput):
        # If a direct command is given: execute if we allow it
        if type(userinput) != str and userinput in self.allowedcommands:
            userinput(document)
            return

        # If a key in our keymap is given: execute it
        if userinput in self.keymap:
            command = self.keymap[userinput]
            command(document)
            return

        # If a key in document.keymap is given: execute if we allow it
        if userinput in document.keymap:
            command = document.keymap[userinput]
            if command in self.allowedcommands:
                command(document)


    def stop(self, document):
        debug('Exiting error mode')
        Mode.stop(self, document)

    def up(self, document):
        self.index = max(0, self.index - 1)

    def down(self, document):
        self.index = min(len(document.errorlist) - 1, self.index + 1)

    def jump_to_error(self, document):
        errorinterval = document.errorlist[self.index][1]
        Selection([errorinterval])(document)

commands.errormode = ErrorMode
