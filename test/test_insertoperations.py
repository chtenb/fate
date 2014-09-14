"""
This module provides testcases for insertoperations.
Auto indentation is covered.
"""
from ..selectors import nextline, previousword
from ..insertoperations import ChangeAfter, ChangeBefore, ChangeInPlace, ChangeAround
from ..undotree import undo
from .basetestcase import BaseTestCase
from ..commandtools import execute
from .. import document
from .. import run

def deactivate(doc):
    document.activedocument = None

class OperatorTest(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        execute(nextline, self.document)

    def test_change_before(self):
        self.document.ui.feedinput(ChangeBefore)
        for char in '\nasdf\b\b \n \n \n\n\b\b\n':
            self.document.ui.feedinput(char)
        self.document.ui.feedinput('Cancel')
        self.document.ui.feedinput(deactivate)
        run()

        expected = '\nas \n \n  \n  \n\nimport sys'
        self.assertEqual(expected, self.document.text[:len(expected)])

        undo(self.document)
        self.assertEqual('import sys\n\n', self.document.text[:12])

    def test_change_after(self):
        self.document.ui.feedinput(ChangeAfter)
        for char in '\nasdf\b\b \n \n \n\n\b\b\n':
            self.document.ui.feedinput(char)
        self.document.ui.feedinput('Cancel')
        self.document.ui.feedinput(deactivate)
        run()

        expected = 'import sys\nas \n \n  \n  \n\n'
        self.assertEqual(expected, self.document.text[:len(expected)])

        undo(self.document)
        self.assertEqual('import sys\n\n', self.document.text[:12])

    def test_change_in_place(self):
        self.document.ui.feedinput(ChangeInPlace)
        for char in '\nasdf\b\b \n \n \n\n\b\b\n':
            self.document.ui.feedinput(char)
        self.document.ui.feedinput('Cancel')
        self.document.ui.feedinput(deactivate)
        run()

        expected = '\nas \n \n  \n  \n\n'
        self.assertEqual(expected, self.document.text[:len(expected)])

        undo(self.document)
        self.assertEqual('import sys\n\n', self.document.text[:12])

    def test_change_around(self):
        self.document.ui.feedinput(ChangeAfter)
        for char in '\n\n  (hi)':
            self.document.ui.feedinput(char)
        self.document.ui.feedinput('Cancel')
        self.document.ui.feedinput(previousword)
        self.document.ui.feedinput(ChangeAround)
        self.document.ui.feedinput('\n')
        self.document.ui.feedinput('Cancel')

        self.document.ui.feedinput(deactivate)
        run()

        expected = 'import sys\n\n  (\n  hi\n  )\n'
        self.assertEqual(expected, self.document.text[:len(expected)])

        undo(self.document)
        undo(self.document)
        self.assertEqual('import sys\n\n', self.document.text[:12])

