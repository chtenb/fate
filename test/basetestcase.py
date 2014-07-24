from unittest import TestCase, main
from ..session import Session
from tempfile import gettempdir
from shutil import copyfile
from os.path import dirname, abspath
from .proxy_userinterface import ProxyUserInterface

class BaseTestCase(TestCase):

    UserInterfaceClass = ProxyUserInterface

    def setUp(self):
        Session.UserInterfaceClass = self.UserInterfaceClass
        source = dirname(abspath(__file__)) + '/sample.py'
        destination = gettempdir() + '/test.py'
        copyfile(source, destination)
        self.session = Session(destination)

    def tearDown(self):
        self.session.quit()

if __name__ == '__main__':
    main()
