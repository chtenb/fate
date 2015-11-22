"""
This module provides testcases for insertoperations.
Auto indentation is covered.
"""
from ..commands import selectnextline, selectpreviousword
from ..insertoperations import changeafter, changebefore, start_changeinplace, start_changearound
from ..undotree import undo
from .basetestcase import BaseTestCase
from .. import document
from .. import run

def deactivate(doc):
    document.activedocument = None

class OperatorTest(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        selectnextline(self.document)

    def test_change_before(self):
        self.document.ui.feedinput(changebefore)
        for char in '\nasdf\b\b \n \n \n\n\b\b\n':
            self.document.ui.feedinput(char)
        self.document.ui.feedinput(self.document.cancelkey)
        self.document.ui.feedinput(deactivate)
        run()

        expected = '\nas \n \n  \n  \n\nimport sys'
        self.assertEqual(expected, self.document.text[:len(expected)])

        undo(self.document)
        self.assertEqual('import sys\n\n', self.document.text[:12])

    def test_change_after(self):
        self.document.ui.feedinput(changeafter)
        for char in '\nasdf\b\b \n \n \n\n\b\b\n':
            self.document.ui.feedinput(char)
        self.document.ui.feedinput(self.document.cancelkey)
        self.document.ui.feedinput(deactivate)
        run()

        expected = 'import sys\nas \n \n  \n  \n\n'
        self.assertEqual(expected, self.document.text[:len(expected)])

        undo(self.document)
        self.assertEqual('import sys\n\n', self.document.text[:12])

    def test_change_in_place(self):
        self.document.ui.feedinput(start_changeinplace)
        for char in '\nasdf\b\b \n \n \n\n\b\b\n':
            self.document.ui.feedinput(char)
        self.document.ui.feedinput(self.document.cancelkey)
        self.document.ui.feedinput(deactivate)
        run()

        expected = '\nas \n \n  \n  \n\n'
        self.assertEqual(expected, self.document.text[:len(expected)])

        undo(self.document)
        self.assertEqual('import sys\n\n', self.document.text[:12])

    def test_change_around(self):
        self.document.ui.feedinput(changeafter)
        for char in '\n\n  (hi)':
            self.document.ui.feedinput(char)
        self.document.ui.feedinput(self.document.cancelkey)
        self.document.ui.feedinput(selectpreviousword)
        self.document.ui.feedinput(start_changearound)
        self.document.ui.feedinput('\n')
        self.document.ui.feedinput(self.document.cancelkey)

        self.document.ui.feedinput(deactivate)
        run()

        expected = 'import sys\n\n  (\n  hi\n  )\n'
        self.assertEqual(expected, self.document.text[:len(expected)])

        undo(self.document)
        undo(self.document)
        self.assertEqual('import sys\n\n', self.document.text[:12])

