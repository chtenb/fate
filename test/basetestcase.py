from unittest import TestCase, main
from ..document import Document
from tempfile import gettempdir
from shutil import copyfile
from os.path import dirname, abspath
from .proxy_userinterface import ProxyUserInterface

class BaseTestCase(TestCase):

    UserInterfaceClass = ProxyUserInterface

    def setUp(self):
        Document.create_userinterface = self.UserInterfaceClass
        source = dirname(abspath(__file__)) + '/sample.py'
        destination = gettempdir() + '/test.py'
        copyfile(source, destination)
        self.document = Document(destination)

    def tearDown(self):
        self.document.quit()

if __name__ == '__main__':
    main()
