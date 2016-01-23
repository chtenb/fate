"""
A concealment allows to replace parts of the text for purposes of improving the view.
Global concealments are concealments that need context, e.g. strings.
Local conceal do not, like plain string replacements, or simple locally checkable
regular expressions.
"""
from logging import debug

from .document import Document
from .event import Event
from .selection import Interval



def init_conceal(doc):
    doc.conceal = Conceal(doc)

    doc.OnGenerateGlobalConceal = Event('OnGenerateGlobalConceal')
    doc.OnGenerateLocalConceal = Event('OnGenerateLocalConceal')

    doc.OnTextChanged.add(doc.conceal.generate_global_substitutions)

    # Example concealment that does not need any context
    doc.OnGenerateLocalConceal.add(conceal_tabs)

    # Examples
    # doc.OnGenerateGlobalConceal.add(conceal_eol)

Document.OnDocumentInit.add(init_conceal)


class Conceal:

    """Functionality for text concealment."""

    def __init__(self, doc):
        self.doc = doc

        # Lists of (interval, new_content) pairs
        self.global_substitutions = []
        self.local_substitutions = []

    def local_substitute(self, interval, newcontent):
        self.local_substitutions.append((interval, newcontent))

    def global_substitute(self, interval, newcontent):
        self.global_substitutions.append((interval, newcontent))

    def generate_local_substitutions(self, viewport_offset, max_length):
        """
        This method is executed on-the-fly when the textview is generated, so it should
        never have to be called from any other place.
        """
        self.local_substitutions = []
        self.doc.OnGenerateLocalConceal.fire(self.doc, viewport_offset, max_length)
        self.local_substitutions.sort()

    def generate_global_substitutions(self, doc):
        """
        This method is by default only executed OnTextChanged.
        """
        self.global_substitutions = []
        self.doc.OnGenerateGlobalConceal.fire(self.doc)
        self.global_substitutions.sort()


def conceal_tabs(doc, start_pos, max_length):
    for i in range(start_pos, start_pos + max_length):
        if i >= len(doc.text):
            break
        if doc.text[i] == '\t':
            # viewstring = ' ' * (doc.tabwidth - 1) + '\u21E5'
            viewstring = ' ' * doc.tabwidth
            doc.conceal.local_substitute(Interval(i, i + 1), viewstring)


def conceal_eol(doc):
    for i in range(len(doc.text)):
        if i >= len(doc.text):
            break
        if doc.text[i] == '\n':
            doc.conceal.global_substitute(Interval(i, i + 1), '$\n')
