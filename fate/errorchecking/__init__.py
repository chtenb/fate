from importlib import import_module
import subprocess
from logging import info

from ..document import Document
from .. import commands

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
