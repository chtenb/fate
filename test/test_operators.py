from ..selectors import nextword
from ..operators import Insert
from ..commands import undo
from .basetestcase import BaseTestCase

class OperatorTest(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        nextword(self.document)(self.document)

    def test_insert(self):
        command = Insert('Foo ')
        command(self.document)
        expected = 'Foo import sys'
        self.assertEqual(expected, self.document.text[:14])

        undo(self.document)
        self.assertEqual('import sys', self.document.text[:10])

