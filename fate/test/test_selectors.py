from ..selection import Interval, Selection
from .. import commands
from ..selecting.misc import get_line_position
from .basetestcase import BaseTestCase

class SelectorTest(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)

    def test_selectall(self):
        commands.selectall(self.doc)
        expected = Selection([Interval(0, len(self.doc.text))])
        self.assertEqual(expected, self.doc.selection)

    def test_next_word(self):
        commands.selectnextword(self.doc)
        expected = Selection([Interval(0, 6)])
        self.assertEqual(expected, self.doc.selection)

    def test_get_line_position(self):
        text = '\n\n\n\n\n'
        for linenumber in range(5):
            self.assertEqual(linenumber, get_line_position(text, linenumber))

        text = '1\n2\n3\n4\n'
