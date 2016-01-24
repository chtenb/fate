from ..import commands
from ..clipboard import copy, paste_before
from .basetestcase import BaseTestCase

class ClipboardTest(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        commands.selectnextword(self.doc)

    def test_paste_before(self):
        copy(self.doc)
        paste_before(self.doc)
        self.assertEqual('importimport', self.doc.text[:12])

        commands.undo(self.doc)
        self.assertEqual('import sys', self.doc.text[:10])

