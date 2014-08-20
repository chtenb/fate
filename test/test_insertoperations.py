"""
This module provides testcases for insertoperations.
Auto indentation is covered.
"""
from ..selectors import nextline, previousword
from ..insertoperations import ChangeAfter, ChangeBefore, ChangeInPlace, ChangeAround
from ..undotree import undo
from .basetestcase import BaseTestCase
from ..commandtools import execute
from .. import run
from .. import document

class OperatorTest(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        execute(nextline, self.document)

    def deactivate(self, doc):
        document.activedocument = None

    def test_change_before(self):
        self.document.ui.feedinput(ChangeBefore)
        for char in '\nasdf\b\b \n \n \n\n\b\b\n':
            self.document.ui.feedinput(char)
        self.document.ui.feedinput('Cancel')
        self.document.ui.feedinput(self.deactivate)
        run()
        expected = '\nas \n \n  \n  \n\nimport sys'
        print('-----------------------------------------')
        print(expected)
        print(self.document.text[:len(expected)])
        print('-----------------------------------------')
        self.assertEqual(expected, self.document.text[:len(expected)])

        undo(self.document)
        self.assertEqual('import sys\n\n', self.document.text[:12])

    def xtest_change_after(self):
        self.document.ui.feedinput(ChangeAfter)
        for char in '\nasdf\b\b \n \n \n\n\b\b\n':
            self.document.ui.feedinput(char)
        self.document.ui.feedinput('Cancel')
        self.document.ui.feedinput(self.deactivate)
        run()
        expected = 'import sys\nas \n \n  \n  \n\n'
        self.assertEqual(expected, self.document.text[:len(expected)])

        undo(self.document)
        self.assertEqual('import sys\n\n', self.document.text[:12])

    def xtest_change_in_place(self):
        self.document.ui.feed('\nasdf\b\b \n \n \n\n\b\b\n')
        execute(ChangeInPlace, self.document)
        expected = '\nas \n \n  \n  \n\n'
        self.assertEqual(expected, self.document.text[:len(expected)])

        undo(self.document)
        self.assertEqual('import sys\n\n', self.document.text[:12])

    def xtest_change_around(self):
        self.document.ui.feed('\n\n  (hi)')
        execute(ChangeAfter, self.document)
        execute(previousword, self.document)
        self.document.ui.feed('\n')
        execute(ChangeAround, self.document)
        expected = 'import sys\n\n  (\n  hi\n  )\n'
        self.assertEqual(expected, self.document.text[:len(expected)])

        undo(self.document)
        self.assertEqual('import sys\n\n', self.document.text[:12])

