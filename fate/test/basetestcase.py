from unittest import TestCase
from .. import document
from tempfile import gettempdir
from .proxy_userinterface import ProxyUserInterface

class BaseTestCase(TestCase):

    create_userinterface = ProxyUserInterface
    sampletext = """import sys

class Foo(Bar):
    def __init__(self):
        pass
        pass

    def start(self):
        print('Start!')
        return 1

"""

    def setUp(self, sampletext=None):
        if sampletext != None:
            self.sampletext = sampletext
        document.Document.create_userinterface = self.create_userinterface
        destination = gettempdir() + '/test.py'
        with open(destination, 'w') as f:
            f.write(self.sampletext)
        self.doc = document.Document(destination)
        document.activedocument = self.doc

    def tearDown(self):
        self.doc.quit()

