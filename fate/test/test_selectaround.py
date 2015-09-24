from ..selection import Interval, Selection
from ..selectaround import select_next_enclosing, select_next_enclosing_char
from .basetestcase import BaseTestCase


class SelectAroundTest(BaseTestCase):

    sampletext = """('hello'{)'hello'}"""

    def setUp(self):
        BaseTestCase.setUp(self)

    def test_find_matching_pair(self):
        doc = self.document
        doc.selection = Selection([Interval(0, 1)])

        select_next_enclosing(doc)
        expected = Selection([Interval(0, 10)])
        self.assertEqual(expected, doc.selection)

        select_next_enclosing(doc)
        expected = Selection([Interval(1, 9)])
        self.assertEqual(expected, doc.selection)

        select_next_enclosing(doc)
        expected = Selection([Interval(1, 8)])
        self.assertEqual(expected, doc.selection)

        select_next_enclosing(doc)
        expected = Selection([Interval(2, 7)])
        self.assertEqual(expected, doc.selection)

        select_next_enclosing(doc)
        expected = Selection([Interval(7, 11)])
        self.assertEqual(expected, doc.selection)
