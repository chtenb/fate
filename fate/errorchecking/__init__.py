from importlib import import_module
import subprocess
from logging import info

from ..document import Document
from .. import commands

# Dependencies
from .. import filetype


class ErrorChecker:

    """Container for formatter configuration."""

    def run(self, document):
        """
        Has to return errors as a dictionary in the following format:
        interval : ('error|warning', '<message>')
        """
        pass


def checkerrors(doc):
    """If doc has a errorchecker, execute it and make results visible."""
    errorchecker = doc.errorchecker
    if errorchecker:
        result = errorchecker.run(doc)
        doc.labeling.update(result)

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
