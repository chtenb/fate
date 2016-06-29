from logging import debug
from .basetestcase import BaseTestCase
from ..selection import Selection, Interval
from ..insertoperations import changeinplace

from ..textview import TextView
from ..text import StringText


def init_concealers(doc):
    doc.OnGenerateLocalConceal.add(show_empty_interval_selections)
    doc.OnGenerateLocalConceal.add(show_selected_newlines)

def show_empty_interval_selections(doc, partial_text):
    for beg, end in doc.selection:
        if beg == end and partial_text.beg <= beg <= partial_text.end:
            doc.conceal.local_substitute(Interval(beg, end), '|')

def show_selected_newlines(doc, partial_text):
    for beg, end in doc.selection:
        if beg == end and partial_text.beg <= beg <= partial_text.end:
            for pos, char in enumerate(doc.text[beg:end]):
                if char == '\n':
                    doc.conceal.local_substitute(Interval(beg + pos, beg + pos + 1), ' \n')


class TestTextView(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)

    def test_creation_without_conceal(self):
        self.helper()

    def test_creation_with_conceal(self):
        init_concealers(self.doc)
        self.helper()

    def test_creation_with_insert_operation(self):
        self.doc.modes.changeinplace(self.doc)
        self.doc.mode.insert(self.doc, '123')
        self.helper()

    def test_creation_with_insert_operation_and_conceal(self):
        init_concealers(self.doc)
        self.doc.modes.changeinplace(self.doc)
        self.doc.mode.insert(self.doc, '123')
        self.helper()

    def helper(self):
        for text in ['', '123456789', '\n\n\n\n\n']:
            text = StringText(text)
            self.doc.text = text
            for selection in [Selection([Interval(0, 0)]),
                              Selection([Interval(0, len(text))])]:
                self.doc.selection = selection
                for width in range(1, 6):
                    TextView.for_entire_text(self.doc, width)
                    for offset in range(max(1, len(text))):
                        for height in range(1, 6):
                            TextView.for_screen(self.doc, width, height, offset)

