from ..document import Document
from ..event import Event

# Dependencies
from .. import filetype

from logging import debug

def init_textview(doc):
    #doc.OnRefreshView = Event()
    doc.view = View(doc)

    doc.OnDocumentInit.add_for_once(doc.view.refresh)

Document.OnDocumentInit.add(init_textview)


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
        #doc.OnRefreshView.fire(doc)

        self.conceal.refresh(self.doc)
        refresh_highlightingview(self.doc)
        refresh_selectionview(self.doc)
        debug('refreshing view')
