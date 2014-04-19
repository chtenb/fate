from unittest import TestCase, main
from ..session import Session
from ..selectors import NextWord
from ..operators import Insert, ChangeAround

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
        action = Insert('Foo ', self.session)
        action(self.session)
        expected = 'Foo import sys'
        self.assertEqual(expected, self.session.text[:14])

    def test_change_around(self):
        action = ChangeAround(self.session)
        action(self.session)
        action.insert(self.session, '({')

        self.assertFalse(self.session.interactionstack.isempty)

        action.proceed(self.session)
        expected = '{(import)} sys'

        self.assertEqual(expected, self.session.text[:14])
        self.assertTrue(self.session.interactionstack.isempty)

if __name__ == '__main__':
    main()
