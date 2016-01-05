from unittest import TestCase
from .basetestcase import BaseTestCase

from ..textview import TextView

class TestTextView(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)

    def test_creation(self):
        textview = TextView(self.doc, 0, 10)

