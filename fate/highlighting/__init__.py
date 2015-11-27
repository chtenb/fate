# Dependencies
from .. import filetype

from importlib import import_module
import logging

from ..document import Document
from ..event import Event


class Highlighting(dict):

    """A Highlighting is a mapping from positions to string labels"""

    def highlight(self, interval, label):
        beg, end = interval
        for position in range(beg, end):
            self[position] = label


def load_highlighting_script(doc):
    """If we have a filetype, try to import the corresponding labeling module."""
    if doc.filetype:
        try:
            module = import_module(__name__ + '.' + doc.filetype)
        except ImportError as e:
            if e.name == doc.filetype: # Catch import error non-recursively
                logging.info('No labeling script found for filetype ' + doc.filetype)
            else:
                raise
        else:
            logging.info('Found labeling script for filetype ' + doc.filetype)
            module.init(doc)


def clear_highlighting(doc):
    doc.highlighting.clear()

def init_highlighting(doc):
    doc.OnGenerateGlobalHighlighting = Event('OnGenerateGlobalHighlighting')
    doc.OnGenerateLocalHighlighting = Event('OnGenerateLocalHighlighting')
    doc.highlighting = Highlighting()

    doc.OnTextChanged.add(clear_highlighting)
    doc.OnTextChanged.add(doc.OnGenerateGlobalHighlighting.fire)

Document.OnDocumentInit.add(init_highlighting)
Document.OnFileTypeLoaded.add(load_highlighting_script)


logging.info('highlighting system loaded')
