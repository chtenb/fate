from unittest import TestCase, main
from ..session import Session
from ..selectors import NextWord
from ..actions import undo
from ..clipboard import copy, paste_before

TEXT = """\
import sys

class Foo(Bar):
    def __init__(self):
        pass
        pass

    def start(self):
        print('Start!')
        return 1
"""

class ClipboardTest(TestCase):
    def setUp(self):
        self.session = Session()
        self.session.text = TEXT
        NextWord(self.session)(self.session)

    def test_paste_before(self):
        copy(self.session)
        paste_before(self.session)
        self.assertEqual('importimport', self.session.text[:12])

        undo(self.session)
        self.assertEqual('import sys', self.session.text[:10])

if __name__ == '__main__':
    main()
