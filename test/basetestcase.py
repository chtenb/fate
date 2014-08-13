# We import fate here as well, to make it possible to run test scripts standalone
#import os
#import sys
#path_to_fate = os.path.dirname(os.path.abspath(__file__)) + '/../'
#sys.path.insert(0, path_to_fate)

from ..session import Session

from unittest import TestCase
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

