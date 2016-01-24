from logging import debug
from .basetestcase import BaseTestCase

from ..textview import TextView


class TestTextView(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)

    def test_creation(self):
        text = '123456789'
        self.doc.text = text

        for width in range(1, 6):
            for height in range(1, 6):
                TextView(self.doc, width, height)

        text = '\n\n\n\n\n'
        self.doc.text = text

        for width in range(1, 6):
            for height in range(1, 6):
                textview = TextView(self.doc, width, height)
                debug(textview)
