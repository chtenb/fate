from ..selection import Interval
from ..selectaround import expand_to_valid_structure, find_nesting_levels
from .basetestcase import BaseTestCase

class SelectAroundTest(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)

    def test_find_matching_pair(self):
        fst, snd = '(', ')'

        with self.subTest():
            string = '()'
            beg, end = 0, 2

            result = find_nesting_levels(string, beg, end, fst, snd)
            expected = (0, 0)
            self.assertEqual(expected, result)

            result = expand_to_valid_structure(string, beg, end, fst, snd)
            expected = None
            self.assertEqual(expected, result)

        with self.subTest():
            string = '()'
            beg, end = 0, 1

            result = find_nesting_levels(string, beg, end, fst, snd)
            expected = (0, 1)
            self.assertEqual(expected, result)

            result = expand_to_valid_structure(string, beg, end, fst, snd)
            expected = Interval(0, 2)
            self.assertEqual(expected, result)

        with self.subTest():
            string = '|(())|'
            beg, end = 0, 6

            result = find_nesting_levels(string, beg, end, fst, snd)
            expected = (0, 0)
            self.assertEqual(expected, result)

            result = expand_to_valid_structure(string, beg, end, fst, snd)
            expected = None
            self.assertEqual(expected, result)

        with self.subTest():
            string = '((|)((|)))'
            beg, end = 2, 7

            result = find_nesting_levels(string, beg, end, fst, snd)
            expected = (1, 2)
            self.assertEqual(expected, result)

            result = expand_to_valid_structure(string, beg, end, fst, snd)
            expected = Interval(0, 10)
            self.assertEqual(expected, result)

