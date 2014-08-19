from unittest import TestCase, main
from .. import document
from tempfile import gettempdir
#from shutil import copyfile
#from os.path import dirname, abspath
from .proxyuserinterface import ProxyUserInterface


class BaseTestCase(TestCase):

    UserInterfaceClass = ProxyUserInterface
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
        document.Document.create_userinterface = self.UserInterfaceClass
        #source = dirname(abspath(__file__)) + '/sample.py'
        #copyfile(source, destination)
        destination = gettempdir() + '/test.py'
        with open(destination, 'w') as fd:
            fd.write(self.sampletext)
        self.document = document.Document(destination)
        document.activedocument = self.document

    def tearDown(self):
        self.document.quit()

