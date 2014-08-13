from .basetestcase import BaseTestCase
from logging import debug

class TextTest(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)

    def test_str(self):
        expected = """import sys

class Foo(Bar):
    def __init__(self):
        pass
        pass

    def start(self):
        print('Start!')
        return 1

"""

        #debug(repr(expected))
        #debug(repr(self.session.text))
        #debug(len(expected))
        #debug(len(self.session.text))
        #debug(expected)
        #debug(self.session.text)
        #debug(self.session.text == expected)
        self.assertEqual(expected, str(self.session.text))

