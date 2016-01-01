from logging import debug

from ..document import Document
from ..event import Event


# Dependencies
from .. import filetype


def init_view(doc):
    doc.OnRefreshView = Event('OnRefreshView')
    doc.view = View(doc)

    # Refresh at least once to ensure a valid state
    # Other refreshes must be done when necessary
    doc.OnDocumentInit.add_for_once(doc.view.refresh)

Document.OnDocumentInit.add(init_view)


from . import conceal
from .highlightingview import refresh_highlightingview
from .selectionview import refresh_selectionview


class View:

    def __init__(self, doc):
        self.doc = doc
        self.conceal = conceal.Conceal(doc)

        self.text = None
        self.selection = None
        self.highlighting = None

        self.viewstart = 0
        self.viewend = 0
        self.viewpos_to_origpos = []
        self.origpos_to_viewpos = []

    # Optional doc argument allows to use this method as event handler
    def refresh(self, doc=None):
        """
        Compute a piece of text for the UI to display.
        Updates textview and the corresponding positions mappings.
        """
        if doc and self.doc != doc:
            raise ValueError('Document passed as argument differs from self.doc')

        self.doc.OnRefreshView.fire(doc)
        self.conceal.refresh(self.doc)
        refresh_highlightingview(self.doc)
        refresh_selectionview(self.doc)
