from importlib import import_module
import logging

from ..document import Document
from ..event import Event

# Dependencies
from .. import filetype


class Labeling(dict):

    """A Labeling is a mapping from the text to string labels"""

    def add(self, interval, label):
        beg, end = interval
        for position in range(beg, end):
            self[position] = label


def load_labeling_script(document):
    """If we have a filetype, try to import the corresponding labeling module."""
    document.OnGenerateLabeling = Event()
    document.labeling = Labeling()

    if document.filetype:
        try:
            module = import_module(__name__[:-len('labeling')] + document.filetype)
        except ImportError as e:
            if e.name == document.filetype:
                logging.info('No labeling script found for filetype ' + document.filetype)
            else:
                raise
        else:
            logging.info('Found labeling script for filetype ' + document.filetype)
            document.OnTextChanged.add(generate_labeling)
            module.init(document)

Document.OnFileTypeLoaded.add(load_labeling_script)


def generate_labeling(document, *args):
    """Create the labeling."""
    document.labeling = Labeling()
    document.OnGenerateLabeling.fire(document)


logging.info('labeling system loaded')
