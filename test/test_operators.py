from unittest import TestCase, main
from ..session import Session
from ..selectors import NextWord
from ..operators import Insert, ChangeAround
from ..actors import undo

TEXT = """\
import sys

class Foo(Bar):
    def __init__(self):
        pass
        pass

    def start(self):
        print('Start!')
        return 1
"""

class OperatorTest(TestCase):
    def setUp(self):
        self.session = Session()
        self.session.text = TEXT
        NextWord(self.session)(self.session)

    def test_insert(self):
        action = Insert('Foo ')
        action(self.session)
        expected = 'Foo import sys'
        self.assertEqual(expected, self.session.text[:14])

        undo(self.session)
        self.assertEqual('import sys', self.session.text[:10])

    def test_change_around(self):
        action = ChangeAround(self.session)
        action(self.session)
        action.interact(self.session, '({')

        self.assertFalse(self.session.interactionstack.isempty)

        action.proceed(self.session)
        expected = '{(import)} sys'

        self.assertEqual(expected, self.session.text[:14])
        self.assertTrue(self.session.interactionstack.isempty)

        undo(self.session)
        self.assertEqual('import sys', self.session.text[:10])

if __name__ == '__main__':
    main()
