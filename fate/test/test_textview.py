from logging import debug
from .basetestcase import BaseTestCase

from ..textview import TextView


class TestTextView(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)

    def test_creation_without_conceal(self):
        for text in ['', '123456789', '\n\n\n\n\n']:
            self.doc.text = text
            for width in range(1, 6):
                TextView.for_entire_text(self.doc, width)
                for offset in range(max(1, len(text))):
                    for height in range(1, 6):
                        TextView.for_screen(self.doc, width, height, offset)
