from ..selection import Interval, Selection
from .. import commands
from .basetestcase import BaseTestCase

class SelectorTest(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)

    def test_selectall(self):
        commands.selectall(self.document)
        expected = Selection([Interval(0, len(self.document.text))])
        self.assertEqual(expected, self.document.selection)

    def test_next_word(self):
        commands.selectnextword(self.document)
        expected = Selection([Interval(0, 6)])
        self.assertEqual(expected, self.document.selection)

