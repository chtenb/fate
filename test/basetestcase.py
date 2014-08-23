from unittest import TestCase
from .. import document
from tempfile import gettempdir
from shutil import copyfile
from os.path import dirname, abspath
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
        #source = dirname(abspath(__file__)) + '/sample.py'
        #copyfile(source, destination)
        destination = gettempdir() + '/test.py'
        copyfile(source, destination)
        self.document = document.Document(destination)
        document.activedocument = self.document

    def tearDown(self):
        self.document.quit()

