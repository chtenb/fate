from unittest import main
from ..selectors import NextWord
from ..operators import Insert
from ..actions import undo
from .basetestcase import BaseTestCase

class OperatorTest(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        NextWord(self.document)(self.document)

    def test_insert(self):
        action = Insert('Foo ')
        action(self.document)
        expected = 'Foo import sys'
        self.assertEqual(expected, self.document.text[:14])

        undo(self.document)
        self.assertEqual('import sys', self.document.text[:10])

