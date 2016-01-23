from unittest import TestCase
from .basetestcase import BaseTestCase

from ..textview import TextView

class TestTextView(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)

    def test_creation(self):
        text='\n\n\n\n\n'
        self.doc.text = text
        textview = TextView(self.doc, 10, 10)
        print(textview.text)
        print('\n'.join(textview.text_as_lines()))
        print(textview.selection)
        print(textview.highlighting)

