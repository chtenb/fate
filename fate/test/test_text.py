import re
from unittest import TestCase
from ..selection import Interval

from ..text import PartialText


class TestText(TestCase):

    def test_regex(self):
        text = PartialText('bcd', 5, 1, 4)
        regex = re.compile('c')
        match = next(text.finditer(regex))
        self.assertEqual(Interval(2, 3), match)

