from importlib import import_module, find_loader
import subprocess
from logging import info
import sys

from ..document import Document
from ..mode import Mode
from .. import commands
from ..selection import Selection
from logging import debug, error

# Dependencies
from .. import filetype

from traceback import extract_tb

class ErrorChecker:

    """Container for formatter configuration."""
    name = '<checkername>'

    def check(self, document):
        """Has to return and errorlist."""
        pass


class ErrorList(list):

    """Docstring for ErrorList. """

    def __init__(self, *args, **kwargs):
        self.current = 0
        self.checkername = ''
        list.__init__(self, *args, **kwargs)


def init_errorlist(document):
    """
    An errorlist is a list of tuples of the form
    (['error'|'warning'], <interval>, <message>)
    """
    document.errorlist = ErrorList()
Document.OnDocumentInit.add(init_errorlist)


def checkerrors(doc):
    """If doc has errorcheckers, try to execute them and make results visible."""
    for checker in doc.errorcheckers:
        try:
            errorlist = ErrorList(checker.check(doc))
            if len(errorlist) == 0:
                continue
            errorlist.checkername = checker.name
            doc.errorlist = errorlist
            for etype, interval, _ in errorlist:
                beg, end = interval
                for pos in range(beg, end):
                    doc.highlighting[pos] = etype
            return
        except IOError:
            # The current error checker is probably not installed
            pass

commands.checkerrors = checkerrors


def load_filetype_errorchecker(doc):
    doc.errorcheckers = []
    if doc.filetype:
        subpackage_name = __name__ + '.' + doc.filetype
        try:
            subpackage = import_module(subpackage_name)
        except ImportError as e:
            # Catch import error nonrecursively
            if e.name == subpackage_name:
                info('No errorchecker scripts found for filetype ' + doc.filetype)
            else:
                raise
        else:
            doc.errorcheckers = subpackage.errorcheckers
            info('Errorchecker scripts found for filetype ' + doc.filetype)

Document.OnFileTypeLoaded.add(load_filetype_errorchecker)

# TODO: turn up, down into commands?


class ErrorMode(Mode):

    """
    Walk around in error list using j/k.
    """

    def __init__(self, doc, callback=None):
        Mode.__init__(self, doc, callback)
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

        checkerrors(doc)
        self.start(doc)

    def processinput(self, doc, userinput):
        # If a direct command is given: execute if we allow it
        if type(userinput) != str and userinput in self.allowedcommands:
            userinput(doc)
            return

        # If a key in our keymap is given: execute it
        if userinput in self.keymap:
            command = self.keymap[userinput]
            command(doc)
            return

        # If a key in doc.keymap is given: execute if we allow it
        if userinput in doc.keymap:
            command = doc.keymap[userinput]
            if command in self.allowedcommands:
                command(doc)

    def stop(self, doc):
        debug('Exiting error mode')
        Mode.stop(self, doc)

    def up(self, doc):
        doc.errorlist.current = max(0, doc.errorlist.current - 1)

    def down(self, doc):
        doc.errorlist.current = min(len(doc.errorlist) - 1, doc.errorlist.current + 1)

    def jump_to_error(self, doc):
        errorinterval = doc.errorlist[doc.errorlist.current][1]
        Selection([errorinterval])(doc)

commands.errormode = ErrorMode
