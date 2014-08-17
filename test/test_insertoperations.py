"""
This module provides testcases for insertoperations.
Auto indentation is covered.
"""
from ..selectors import nextline, previousword
from ..insertoperations import ChangeAfter, ChangeBefore, ChangeInPlace, ChangeAround
from ..commands import undo
from .basetestcase import BaseTestCase
from ..commandtools import execute

class OperatorTest(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        execute(nextline, self.document)

    def test_change_after(self):
        self.document.ui.feed('\nasdf\b\b \n \n \n\n\b\b\n')
        execute(ChangeAfter, self.document)
        expected = 'import sys\nas \n \n  \n  \n\n'
        self.assertEqual(expected, self.document.text[:len(expected)])

        undo(self.document)
        self.assertEqual('import sys\n\n', self.document.text[:12])

    def test_change_before(self):
        self.document.ui.feed('\nasdf\b\b \n \n \n\n\b\b\n')
        execute(ChangeBefore, self.document)
        expected = '\nas \n \n  \n  \n\nimport sys'
        self.assertEqual(expected, self.document.text[:len(expected)])

        undo(self.document)
        self.assertEqual('import sys\n\n', self.document.text[:12])

    def test_change_in_place(self):
        self.document.ui.feed('\nasdf\b\b \n \n \n\n\b\b\n')
        execute(ChangeInPlace, self.document)
        expected = '\nas \n \n  \n  \n\n'
        self.assertEqual(expected, self.document.text[:len(expected)])

        undo(self.document)
        self.assertEqual('import sys\n\n', self.document.text[:12])

    def test_change_around(self):
        self.document.ui.feed('\n\n  (hi)')
        execute(ChangeAfter, self.document)
        execute(previousword, self.document)
        self.document.ui.feed('\n')
        execute(ChangeAround, self.document)
        expected = 'import sys\n\n  (\n  hi\n  )\n'
        self.assertEqual(expected, self.document.text[:len(expected)])

        undo(self.document)
        self.assertEqual('import sys\n\n', self.document.text[:12])

