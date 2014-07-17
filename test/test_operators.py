from unittest import main
from ..selectors import NextWord
from ..operators import Insert
from ..actions import undo
from .basetestcase import BaseTestCase

class OperatorTest(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        NextWord(self.session)(self.session)

    def test_insert(self):
        action = Insert('Foo ')
        action(self.session)
        expected = 'Foo import sys'
        self.assertEqual(expected, self.session.text[:14])

        undo(self.session)
        self.assertEqual('import sys', self.session.text[:10])

if __name__ == '__main__':
    main()
