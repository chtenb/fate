"""
This module provides testcases for insertoperations.
Auto indentation is covered.
"""
from unittest import main
from ..selectors import NextLine
from ..insertoperations import ChangeAfter, ChangeBefore, ChangeAround
from ..actions import undo
from .basetestcase import BaseTestCase
from ..actiontools import execute

class OperatorTest(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        execute(NextLine, self.session)

    def test_change_after(self):
        self.session.ui.feed('\nasdf\b\b \n \n \n\n\b\b\n')
        execute(ChangeAfter, self.session)
        expected = 'import sys\nas \n \n  \n  \n\n'
        self.assertEqual(expected, self.session.text[:len(expected)])

        undo(self.session)
        self.assertEqual('import sys\n\n', self.session.text[:12])

if __name__ == '__main__':
    main()
