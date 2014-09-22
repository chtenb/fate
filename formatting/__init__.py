from importlib import import_module
import logging
import subprocess

from ..selectors import selectall
from ..operation import Operation
from ..document import Document
from .. import filetype_system
from .. import commands


class Formatter:

    """Container for formatter configuration."""

    def __init__(self, executable, arguments):
        self.executable = executable
        self.arguments = arguments


def formattext(document):
    """If document has a formatter, execute it and replace text with the result."""
    formatter = document.formatter
    if formatter:
        # Execute formatter
        # TODO
        process = subprocess.Popen([formatter.executable, formatter.arguments],
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   universal_newlines=True)
        newtext, errors = process.communicate(document.text)

        # Replace text with formatted text
        selectall(document)
        operation = Operation(document, newcontent=[newtext])
        operation(document)
commands.formattext = formattext


def load_filetype_formatter(document):
    if document.filetype:
        try:
            module = import_module(__name__ + '.' + document.filetype)
        except ImportError:
            logging.info('No formatter script found for filetype ' + document.filetype)
        else:
            logging.info('Formatter script found for filetype ' + document.filetype)
            document.formatter = module.formatter

Document.OnFileTypeLoaded.add(load_filetype_formatter)
