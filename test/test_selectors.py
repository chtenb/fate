from unittest import TestCase, main
from ..session import Session
from ..selection import Interval, Selection
from ..selectors import SelectEverything, NextWord, find_matching_pair

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

    def test_find_matching_pair1(self):
        string = 'ab(cde)fgh'
        fst = '('
        snd = ')'
        pos = 4
        result = find_matching_pair(string, pos, fst, snd)
        expected = Interval(2, 7)
        self.assertEqual(expected, result)

    def test_find_matching_pair2(self):
        string = 'a((b)c)d'
        fst = '('
        snd = ')'
        pos = 5
        result = find_matching_pair(string, pos, fst, snd)
        expected = Interval(1, 7)
        self.assertEqual(expected, result)

    def test_find_matching_pair3(self):
        string = 'a((b)c)d'
        fst = '('
        snd = ')'
        pos = 0
        result = find_matching_pair(string, pos, fst, snd)
        expected = None
        self.assertEqual(expected, result)




if __name__ == '__main__':
    main()
