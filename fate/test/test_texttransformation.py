from unittest import TestCase
from ..texttransformation import (IntervalMapping, IntervalSubstitution, TextTransformation,
                                  PartialTextTransformation)
from ..selection import Interval, Selection
from ..text import StringText, PartialText
from random import randint


class TestPartialTextTransformation(TestCase):

    def test_transform(self):
        text = StringText('12345')
        partial_text = PartialText.from_text(text, 2, 5)
        selection = Selection([Interval(0, 1), Interval(2, 2), Interval(3, 4)])
        replacements = ['x', 'y', '']
        transformation = TextTransformation(selection, replacements, text)
        partial_transformation = PartialTextTransformation(transformation, 2, 4, partial_text)
        result = partial_text.transform(partial_transformation)
        self.assertEqual('y35', result)

        # Test inverse
        inverse = partial_transformation.inverse(result)
        inverse_result = result.transform(inverse)
        self.assertEqual('345', inverse_result)


class TestTextTransformation(TestCase):

    def test_transform(self):
        text = StringText('12345')
        selection = Selection([Interval(0, 1), Interval(2, 2), Interval(3, 4)])
        replacements = ['x', 'y', '']
        transformation = TextTransformation(selection, replacements, text)
        result = text.transform(transformation)
        self.assertEqual('x2y35', result)

        # Test inverse
        inverse = transformation.inverse(result)
        inverse_result = result.transform(inverse)
        self.assertEqual(text, inverse_result)


class TestIntervalMapping(TestCase):

    def test_death(self):
        # Test random sets of substitutions and intervals to check for exceptions
        for test_nr in range(0, 1000):
            substitutions = []
            lowerbound = 0
            for _ in range(randint(0, 5)):
                beg = randint(lowerbound, 10)
                end = randint(beg, 10)
                length = randint(0, 3)
                s = IntervalSubstitution(Interval(beg, end), length)
                substitutions.append(s)
                lowerbound = end

            mapping = IntervalMapping(substitutions)
            lowerbound = 0
            selection = Selection()
            for _ in range(randint(0, 5)):
                beg = randint(lowerbound, 10)
                end = randint(beg, 10)
                selection.add(Interval(beg, end))
                lowerbound = end

            mapping[selection]

            new_intervals = [mapping[interval] for interval in selection]

            # Test for disjointness and order preservingness
            last_end = 0
            for beg, end in new_intervals:
                self.assertTrue(last_end <= beg)

    def test_intervalmapping_getitem(self):
        # Test positions before and after substitutions
        mapping = IntervalMapping([])
        for beg in range(3):
            for end in range(beg, 3):
                interval = Interval(beg, end)
                self.assertEqual(interval, mapping[interval])

        a = IntervalSubstitution(Interval(1, 3), 3)
        mapping = IntervalMapping([a])
        self.assertEqual(Interval(0, 1), mapping[Interval(0, 1)])
        self.assertEqual(Interval(4, 6), mapping[Interval(3, 5)])

        # Test positions inside substitutions
        a = IntervalSubstitution(Interval(0, 2), 3)
        mapping = IntervalMapping([a])
        self.assertEqual(0, mapping[0])
        self.assertEqual(0, mapping[1])
        self.assertEqual(3, mapping[2])

        # Test positions inbetween substitutions
        a = IntervalSubstitution(Interval(0, 2), 3)
        b = IntervalSubstitution(Interval(6, 6), 3)
        mapping = IntervalMapping([a, b])
        self.assertEqual(3, mapping[2])
        self.assertEqual(4, mapping[3])
        self.assertEqual(5, mapping[4])
        self.assertEqual(6, mapping[5])
        self.assertEqual(7, mapping[6])

        # Test some intervals
        a = IntervalSubstitution(Interval(0, 2), 3)
        b = IntervalSubstitution(Interval(4, 4), 3)
        c = IntervalSubstitution(Interval(4, 6), 0)
        mapping = IntervalMapping([a, b, c])

        self.assertEqual(Interval(0, 3), mapping[Interval(0, 2)])
        self.assertEqual(Interval(0, 0), mapping[Interval(1, 1)])
        self.assertEqual(Interval(0, 0), mapping[Interval(0, 0)])

        # TODO:
        # Our inner mapping representation is wrong
        # We have to preserve the substitutions as some kind of tuples, to do the snapping
        # correct. Now we are always snapping down, which is wrong.
        # Possibilities:
        # - represent positions inside a substitution by a None value
        #   Cons: need to iterate to obtain values
        # - represent positions inside a substitution by a tuple
        #   Cons: confusion with insertions
        # - represent positions inside a substitution by a 3-tuple containing a None value
        #   Cons: ugly
        #

        # Test interval snapping w.r.t. insertions
        # self.assertEqual(Interval(0, 5), mapping[Interval(1, 4)])
        # self.assertEqual(Interval(5, 8), mapping[Interval(4, 4)])
        # self.assertEqual(Interval(3, 4), mapping[Interval(1, 3)])

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
