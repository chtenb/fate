"""A script to execute some tests."""
import os
import sys

# Make sure fate can be imported anywhere (also from the user script).
path_to_fate = os.path.dirname(os.path.abspath(__file__)) + '/../../'
sys.path.insert(0, path_to_fate)

import pdb
import fate

from fate.selection import *

x = Interval(1, 3)
y = Interval(2, 4)

#print(x + y)

s = Selection()
s.add(x)
print(s)
print(s+y)
print(y+s)
#s.add(y)
#t = s+y

#for i in t:
    #print (i)
