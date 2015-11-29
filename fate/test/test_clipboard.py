from ..import commands
from ..clipboard import copy, paste_before
from .basetestcase import BaseTestCase

class ClipboardTest(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        commands.selectnextword(self.document)

    def test_paste_before(self):
        copy(self.document)
        paste_before(self.document)
        self.assertEqual('importimport', self.document.text[:12])

        commands.undo(self.document)
        self.assertEqual('import sys', self.document.text[:10])

