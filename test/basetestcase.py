from unittest import TestCase, main
from .. import document
from tempfile import gettempdir
from shutil import copyfile
from os.path import dirname, abspath
from .proxy_userinterface import ProxyUserInterface

class BaseTestCase(TestCase):

    UserInterfaceClass = ProxyUserInterface

    def setUp(self):
        document.Document.create_userinterface = self.UserInterfaceClass
        source = dirname(abspath(__file__)) + '/sample.py'
        destination = gettempdir() + '/test.py'
        copyfile(source, destination)
        self.document = document.Document(destination)
        document.activedocument = self.document

    def tearDown(self):
        self.document.quit()

if __name__ == '__main__':
    main()
