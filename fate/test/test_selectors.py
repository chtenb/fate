from ..selection import Interval, Selection
from ..commands import selectall, selectnextword
from .basetestcase import BaseTestCase

class SelectorTest(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)

    def test_selectall(self):
        selectall(self.document)
        expected = Selection([Interval(0, len(self.document.text))])
        self.assertEqual(expected, self.document.selection)

    def test_next_word(self):
        selectnextword(self.document)
        expected = Selection([Interval(0, 6)])
        self.assertEqual(expected, self.document.selection)

