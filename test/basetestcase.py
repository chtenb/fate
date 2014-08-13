# We import fate here as well, to make it possible to run test scripts standalone
#import os
#import sys
#path_to_fate = os.path.dirname(os.path.abspath(__file__)) + '/../'
#sys.path.insert(0, path_to_fate)

from ..session import Session

from unittest import TestCase
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
        Session.UserInterfaceClass = self.UserInterfaceClass
        #source = dirname(abspath(__file__)) + '/sample.py'
        #copyfile(source, destination)
        destination = gettempdir() + '/test.py'
        with open(destination, 'w') as fd:
            fd.write(self.sampletext)
        self.session = Session(destination)

    def tearDown(self):
        self.session.quit()
