from unittest import TestCase
from ..texttransformation import IntervalMapping, IntervalSubstitution, TextTransformation
from ..selection import Interval, Selection
from random import randint


class TestInterval(TestCase):

    def test_immutability(self):
        interval = Interval(0, 1)
        with self.assertRaises(AttributeError):
            interval.beg = 4
        with self.assertRaises(TypeError):
            interval[0] = 4
        with self.assertRaises(AttributeError):
            interval.foo = 4

class TestSelection(TestCase):
    ...
