from unittest import main
from ..selectors import NextWord
from ..actions import undo
from ..clipboard import copy, paste_before
from .basetestcase import BaseTestCase

class ClipboardTest(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        NextWord(self.session)(self.session)

    def test_paste_before(self):
        copy(self.session)
        paste_before(self.session)
        self.assertEqual('importimport', self.session.text[:12])

        undo(self.session)
        self.assertEqual('import sys', self.session.text[:10])

if __name__ == '__main__':
    main()
