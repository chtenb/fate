from unittest import TestCase
from ..texttransformation import IntervalMapping, IntervalSubstitution
from ..selection import Interval


class TestNavigation(TestCase):

    def test_intervalmapping_creation(self):
        # Test no substitutions at all
        mapping = IntervalMapping([])
        self.assertListEqual(mapping._innermapping, [0])

        # Test empty insertions
        a = IntervalSubstitution(Interval(0, 0), 0)
        b = IntervalSubstitution(Interval(2, 2), 0)
        c = IntervalSubstitution(Interval(4, 4), 0)

        mapping = IntervalMapping([a])
        self.assertListEqual(mapping._innermapping, [0])

        mapping = IntervalMapping([b])
        self.assertListEqual(mapping._innermapping, [0])

        mapping = IntervalMapping([c])
        self.assertListEqual(mapping._innermapping, [0])

        mapping = IntervalMapping([a, b, c])
        self.assertListEqual(mapping._innermapping, [0])

        # Test insertion, at start, middle and end and all together
        a = IntervalSubstitution(Interval(0, 0), 1)
        b = IntervalSubstitution(Interval(2, 2), 1)
        c = IntervalSubstitution(Interval(4, 4), 1)

        mapping = IntervalMapping([a])
        self.assertListEqual(mapping._innermapping, [(0, 1)])

        mapping = IntervalMapping([b])
        self.assertListEqual(mapping._innermapping, [(2, 3)])

        mapping = IntervalMapping([c])
        self.assertListEqual(mapping._innermapping, [(4, 5)])

        mapping = IntervalMapping([a, b, c])
        self.assertListEqual(mapping._innermapping, [(0, 1), 2, (3, 4), 5, (6, 7)])

        # Test deletion, at start, middle and end and all together
        a = IntervalSubstitution(Interval(0, 1), 0)
        b = IntervalSubstitution(Interval(2, 3), 0)
        c = IntervalSubstitution(Interval(3, 4), 0)

        mapping = IntervalMapping([a])
        self.assertListEqual(mapping._innermapping, [0, 0])

        mapping = IntervalMapping([b])
        self.assertListEqual(mapping._innermapping, [2, 2])

        mapping = IntervalMapping([c])
        self.assertListEqual(mapping._innermapping, [3, 3])

        mapping = IntervalMapping([a, b, c])
        self.assertListEqual(mapping._innermapping, [0, 0, 1, 1, 1])

        # Test substition of length 1, at start, middle and end and all together
        a = IntervalSubstitution(Interval(0, 1), 1)
        b = IntervalSubstitution(Interval(2, 3), 1)
        c = IntervalSubstitution(Interval(3, 4), 1)

        mapping = IntervalMapping([a])
        self.assertListEqual(mapping._innermapping, [0, 1])

        mapping = IntervalMapping([b])
        self.assertListEqual(mapping._innermapping, [2, 3])

        mapping = IntervalMapping([c])
        self.assertListEqual(mapping._innermapping, [3, 4])

        mapping = IntervalMapping([a, b, c])
        self.assertListEqual(mapping._innermapping, [0, 1, 2, 3, 4])

        # Test substition of more arbitrary length, at start, middle and end and all together
        a = IntervalSubstitution(Interval(0, 0), 2)
        b = IntervalSubstitution(Interval(1, 2), 3)
        c = IntervalSubstitution(Interval(2, 4), 1)
        d = IntervalSubstitution(Interval(4, 6), 0)

        mapping = IntervalMapping([a])
        self.assertListEqual(mapping._innermapping, [(0, 2)])

        mapping = IntervalMapping([b])
        self.assertListEqual(mapping._innermapping, [1, 4])

        mapping = IntervalMapping([c])
        self.assertListEqual(mapping._innermapping, [2, 2, 3])

        mapping = IntervalMapping([d])
        self.assertListEqual(mapping._innermapping, [4, 4, 4])

        mapping = IntervalMapping([a, b, c, d])
        self.assertListEqual(mapping._innermapping, [(0, 2), 3, 6, 6, 7, 7, 7])

        # Test multiple insertions at the same position
        a = IntervalSubstitution(Interval(2, 2), 1)
        b = IntervalSubstitution(Interval(2, 2), 2)
        c = IntervalSubstitution(Interval(2, 2), 3)

        mapping = IntervalMapping([a, b, c])
        self.assertListEqual(mapping._innermapping, [(2, 8)])

        # Test substitutions that are overlapping or in non sorted order
        a = IntervalSubstitution(Interval(0, 2), 1)
        b = IntervalSubstitution(Interval(1, 2), 1)
        c = IntervalSubstitution(Interval(0, 3), 1)
        d = IntervalSubstitution(Interval(3, 3), 1)
        self.assertRaises(AssertionError, lambda: IntervalMapping([a, b]))
        self.assertRaises(AssertionError, lambda: IntervalMapping([a, c]))
        self.assertRaises(AssertionError, lambda: IntervalMapping([d, a]))

