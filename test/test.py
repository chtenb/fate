"""A script to execute some tests."""
import os
import sys

# Make sure fate can be imported anywhere (also from the user script).
path_to_fate = os.path.dirname(os.path.abspath(__file__)) + '/../../'
sys.path.insert(0, path_to_fate)

import pdb
import fate
from fate.session import Session
from fate import operators, selectors
s = Session()

operators.change_after('test123', 0)(s)
operators.change_after('Boo', 0)(s)
operators.change_after('Baa', 0)(s)
s.actiontree.undo()
operators.change_after('Baa', 0)(s)
s.actiontree.undo()
s.actiontree.undo()
operators.change_after('Baa', 0)(s)
s.actiontree.undo()
print(s.actiontree.pretty_print())
#pdb.set_trace()

