from ..selection import Interval, Selection
from .. import commands
from ..selecting.misc import get_line_position
from ..selecting.selectpattern import selectfullline, selectindent
from unittest import TestCase

class TestSelectPattern(TestCase):
    def test_selectfullline(self):
        text = '123'

        expected = Interval(0, 3)
        self.assertEqual(expected, selectfullline(text, Interval(0, 0)))
        self.assertEqual(expected, selectfullline(text, Interval(0, 3)))
        self.assertEqual(expected, selectfullline(text, Interval(1, 1)))
        self.assertEqual(expected, selectfullline(text, Interval(3, 3)))

    def test_selectindent(self):
        text = '123'

        expected = Interval(0, 0)
        self.assertEqual(expected, selectindent(text, Interval(0, 0)))
        self.assertEqual(expected, selectindent(text, Interval(0, 3)))
        self.assertEqual(expected, selectindent(text, Interval(1, 1)))
        self.assertEqual(expected, selectindent(text, Interval(3, 3)))

        text = ' 12'
        expected = Interval(0, 1)
        self.assertEqual(expected, selectindent(text, Interval(0, 0)))
        self.assertEqual(expected, selectindent(text, Interval(0, 3)))
        self.assertEqual(expected, selectindent(text, Interval(1, 1)))
        self.assertEqual(expected, selectindent(text, Interval(3, 3)))

        text = '\n\n\n'
        self.assertEqual(Interval(0, 0), selectindent(text, Interval(0, 0)))
        self.assertEqual(Interval(0, 0), selectindent(text, Interval(0, 3)))
        self.assertEqual(Interval(1, 1), selectindent(text, Interval(1, 1)))
        self.assertEqual(Interval(3, 3), selectindent(text, Interval(3, 3)))
