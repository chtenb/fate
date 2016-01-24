from ..selection import Interval, Selection
from ..selecting.selectdelimited import (select_next_delimiting, select_next_delimiting_char,
                                         select_previous_delimiting)
from .basetestcase import BaseTestCase


class SelectAroundTest(BaseTestCase):

    sampletext = """('hello'{)'hello'}()"""

    def setUp(self):
        BaseTestCase.setUp(self)

    def test_find_matching_pair(self):
        doc = self.doc
        doc.selection = Selection([Interval(0, 1)])

        select_next_delimiting(doc)
        expected = Selection([Interval(0, 10)])
        self.assertEqual(expected, doc.selection)

        select_next_delimiting(doc)
        expected = Selection([Interval(1, 9)])
        self.assertEqual(expected, doc.selection)

        select_next_delimiting(doc)
        expected = Selection([Interval(1, 8)])
        self.assertEqual(expected, doc.selection)

        select_next_delimiting(doc)
        expected = Selection([Interval(2, 7)])
        self.assertEqual(expected, doc.selection)

        select_next_delimiting(doc)
        expected = Selection([Interval(7, 11)])
        self.assertEqual(expected, doc.selection)

        select_next_delimiting_char(doc, char='(')
        expected = Selection([Interval(18, 20)])
        self.assertEqual(expected, doc.selection)

        select_next_delimiting_char(doc, char='(')
        expected = Selection([Interval(19, 19)])
        self.assertEqual(expected, doc.selection)

        select_previous_delimiting(doc)
        expected = Selection([Interval(18, 20)])
        self.assertEqual(expected, doc.selection)
