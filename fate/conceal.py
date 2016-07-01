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

    # FIXME: find a moment for global generations to be generated, or do it async
    # doc.OnTextChanged.add(doc.conceal.generate_global_substitutions)

    # Example concealment that does not need any context
    doc.OnGenerateLocalConceal.add(conceal_tabs)
    doc.OnGenerateLocalConceal.add(conceal_eol)

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

    def generate_local_substitutions(self, textview):
        """
        This method is executed on-the-fly when the textview is generated, so it should
        never have to be called from any other place.
        """
        self.local_substitutions = []
        self.doc.OnGenerateLocalConceal.fire(self.doc, textview)
        self.local_substitutions.sort()

    def generate_global_substitutions(self, textview):
        """
        This method is by default only executed OnTextChanged.
        """
        self.global_substitutions = []
        self.doc.OnGenerateGlobalConceal.fire(self.doc, textview)
        self.global_substitutions.sort()


def conceal_tabs(doc, textview):
    partial_text = textview.text_after_user_operation
    for i in range(partial_text.beg, partial_text.end):
        if partial_text[i] == '\t':
            # viewstring = ' ' * (doc.tabwidth - 1) + '\u21E5'
            viewstring = ' ' * doc.tabwidth
            doc.conceal.local_substitute(Interval(i, i + 1), viewstring)


def conceal_eol(doc, textview):
    partial_text = textview.text_after_user_operation
    for i in range(partial_text.beg, partial_text.end):
        if partial_text[i] == '\n':
            doc.conceal.local_substitute(Interval(i, i + 1), '$\n')


# TODO: different highlighting for empty interval selections?
# TODO: Also show between adjacent non-empty intervals
def show_empty_interval_selections(doc, textview):
    partial_text = textview.text_after_user_operation
    for beg, end in textview.selection_after_user_operation:
        if beg == end and partial_text.beg <= beg <= partial_text.end:
            doc.conceal.local_substitute(Interval(beg, end), '|')


def show_selected_newlines(doc, textview):
    partial_text = textview.text_after_user_operation
    for beg, end in textview.selection_after_user_operation:
        if beg == end and partial_text.beg <= beg <= partial_text.end:
            for pos, char in enumerate(partial_text[Interval(beg, end)]):
                if char == '\n':
                    doc.conceal.local_substitute(Interval(beg + pos, beg + pos + 1), ' \n')


def show_eof(doc, textview):
    partial_text = textview.text_after_user_operation
    textlength = len(doc.text)
    if partial_text.end == textlength:
        doc.conceal.local_substitute(Interval(textlength, textlength), 'EOF')
