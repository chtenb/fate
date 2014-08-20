from unittest import main
from ..selection import Interval, Selection
from ..selectors import selectall, nextword, find_matching_pair
from .basetestcase import BaseTestCase

class SelectorTest(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)

    def test_selectall(self):
        selectall(self.document)
        expected = Selection([Interval(0, len(self.document.text))])
        self.assertEqual(expected, self.document.selection)

    def test_next_word(self):
        command = nextword(self.document)
        command(self.document)
        expected = Selection([Interval(0, 6)])
        self.assertEqual(expected, self.document.selection)

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

