from unittest import TestCase, main
from ..session import Session

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

class BaseTestCase(TestCase):
    def setUp(self):
        self.session = Session()
        self.session.text = TEXT

    def tearDown(self):
        self.session.quit()

if __name__ == '__main__':
    main()
