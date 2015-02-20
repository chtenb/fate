from importlib import import_module
import logging

from ..document import Document
from ..event import Event
from .labeling import Labeling

# Dependencies
from .. import filetype


def load_labeling_script(document):
    """If we have a filetype, try to import the corresponding labeling module."""
    document.OnGenerateLabeling = Event()

    if document.filetype:
        try:
            module = import_module(__name__ + '.' + document.filetype)
        except ImportError:
            logging.info('No labeling script found for filetype ' + document.filetype)
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
