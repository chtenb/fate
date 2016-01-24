from ..operators import Insert
from .. import commands
from .basetestcase import BaseTestCase

class OperatorTest(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        commands.selectnextword(self.doc)

    def test_insert(self):
        command = Insert('Foo ')
        command(self.doc)
        expected = 'Foo import sys'
        self.assertEqual(expected, self.doc.text[:14])

        commands.undo(self.doc)
        self.assertEqual('import sys', self.doc.text[:10])

