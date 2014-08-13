"""
This module provides testcases for insertoperations.
Auto indentation is covered.
"""
from .basetestcase import BaseTestCase
from ..selectors import NextLine, PreviousWord
from ..insertoperations import ChangeAfter, ChangeBefore, ChangeInPlace, ChangeAround
from ..actions import undo
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

    def test_change_before(self):
        self.session.ui.feed('\nasdf\b\b \n \n \n\n\b\b\n')
        execute(ChangeBefore, self.session)
        expected = '\nas \n \n  \n  \n\nimport sys'
        self.assertEqual(expected, self.session.text[:len(expected)])

        undo(self.session)
        self.assertEqual('import sys\n\n', self.session.text[:12])

    def test_change_in_place(self):
        self.session.ui.feed('\nasdf\b\b \n \n \n\n\b\b\n')
        execute(ChangeInPlace, self.session)
        expected = '\nas \n \n  \n  \n\n'
        self.assertEqual(expected, self.session.text[:len(expected)])

        undo(self.session)
        self.assertEqual('import sys\n\n', self.session.text[:12])

    def test_change_around(self):
        self.session.ui.feed('\n\n  (hi)')
        execute(ChangeAfter, self.session)
        execute(PreviousWord, self.session)
        self.session.ui.feed('\n')
        execute(ChangeAround, self.session)
        expected = 'import sys\n\n  (\n  hi\n  )\n'
        self.assertEqual(expected, self.session.text[:len(expected)])

        undo(self.session)
        self.assertEqual('import sys\n\n', self.session.text[:12])

