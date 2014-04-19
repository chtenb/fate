"""A script to execute some tests."""
import os
import sys
from unittest import TestCase

# Make sure fate can be imported anywhere (also from the user script).
path_to_fate = os.path.dirname(os.path.abspath(__file__)) + '/../../'
sys.path.insert(0, path_to_fate)

from fate.session import Session

class MyTest(TestCase):
    def setUp(self):
        self.session = Session()
