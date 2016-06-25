"""
This module provides testcases for insertoperations.
Auto indentation is covered.
"""
from .. import commands
from ..insertoperations import changeafter, changebefore, changeinplace, changearound
from ..undotree import undo
from .basetestcase import BaseTestCase
from .. import document
from .. import run

def deactivate(doc):
    document.activedocument = None

class OperatorTest(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        commands.selectnextline(self.doc)

    def test_change_in_place(self):
        self.doc.ui.feedinput(changeinplace)
        for char in '\nasdf\b\b \n \n \n\n\b\b\n':
            self.doc.ui.feedinput(char)
        self.doc.ui.feedinput(self.doc.cancelkey)
        self.doc.ui.feedinput(deactivate)
        run()

        expected = '\nas \n \n  \n  \n\n'
        self.assertEqual(expected, self.doc.text[:len(expected)])

        undo(self.doc)
        self.assertEqual('import sys\n\n', self.doc.text[:12])

    def test_change_before(self):
        self.doc.ui.feedinput(changebefore)
        for char in '\nasdf\b\b \n \n \n\n\b\b\n':
            self.doc.ui.feedinput(char)
        self.doc.ui.feedinput(self.doc.cancelkey)
        self.doc.ui.feedinput(deactivate)
        run()

        expected = '\nas \n \n  \n  \n\nimport sys'
        self.assertEqual(expected, self.doc.text[:len(expected)])

        undo(self.doc)
        self.assertEqual('import sys\n\n', self.doc.text[:12])

    def test_change_after(self):
        self.doc.ui.feedinput(changeafter)
        for char in '\nasdf\b\b \n \n \n\n\b\b\n':
            self.doc.ui.feedinput(char)
        self.doc.ui.feedinput(self.doc.cancelkey)
        self.doc.ui.feedinput(deactivate)
        run()

        expected = 'import sys\nas \n \n  \n  \n\n'
        self.assertEqual(expected, self.doc.text[:len(expected)])

        undo(self.doc)
        self.assertEqual('import sys\n\n', self.doc.text[:12])

    def test_change_around(self):
        self.doc.ui.feedinput(changeafter)
        for char in '\n\n  (hi)':
            self.doc.ui.feedinput(char)
        self.doc.ui.feedinput(self.doc.cancelkey)
        self.doc.ui.feedinput(commands.selectpreviousword)
        self.doc.ui.feedinput(changearound)
        self.doc.ui.feedinput('\n')
        self.doc.ui.feedinput(self.doc.cancelkey)

        self.doc.ui.feedinput(deactivate)
        run()

        expected = 'import sys\n\n  (\n  hi\n  )\n'
        self.assertEqual(expected, self.doc.text[:len(expected)])

        undo(self.doc)
        undo(self.doc)
        self.assertEqual('import sys\n\n', self.doc.text[:12])

