from unittest import TestCase, main
from ..session import Session
from ..selection import Interval, Selection
from ..selectors import SelectEverything, NextWord

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

class SelectorTest(TestCase):
    def setUp(self):
        self.session = Session()
        self.session.text = TEXT

    def test_select_everything(self):
        action = SelectEverything(self.session)
        action(self.session)
        expected = Selection([Interval(0, len(TEXT))])
        self.assertEqual(expected, self.session.selection)

    def test_next_word(self):
        action = NextWord(self.session)
        action(self.session)
        expected = Selection([Interval(0, 6)])
        self.assertEqual(expected, self.session.selection)

if __name__ == '__main__':
    main()
