from ..document import Document
from ..event import Event
from .. import filetype_system
from .labeling import Labeling
from importlib import import_module
import logging

Document.OnGenerateLabeling = Event()
Document.labeling = Labeling()


def load_filetype_syntax(document):
    """If we have a filetype, try to import the corresponding labeling module."""
    if document.filetype:
        try:
            import_module(__name__ + '.' + document.filetype)
        except ImportError:
            logging.info('No labeling script found for filetype ' + document.filetype)
        else:
            document.OnTextChanged.add(generate_labeling)
            document.OnRead.add(generate_labeling)


def generate_labeling(document, *args):
    """Create the labeling."""
    document.labeling = Labeling()
    document.OnGenerateLabeling.fire(document)

Document.OnDocumentInit.add(load_filetype_syntax)

logging.info('labeling system loaded')
