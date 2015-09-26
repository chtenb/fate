"""
This subpackage contains all kinds of commands related to make selections.
We distinguish between functions that work selection-wise (global selectors)
and function that work interval-wise (local selectors).
Furthermore we have selectors that are based on regular expressions.

Selectors may return None, in which case the document should not be affected.
Selectors may also return a result which is identical to the previous selection.
The code that executes the command may want to check if this is the case, before applying.

Because it is often handy to use selectors as building blocks for other computations,
selectors return their result as a selection instead of executing them immediately.
Secondly, one can pass a selection which should be used as starting point
for the selector instead of the current selection of the document.
Because of this, it is a good habit to only decorate the function that is placed in
the commands module, not the function itself.
"""
from enum import Enum
from .. import commands


class SelectModes(Enum):
    normal = 'normal'
    head = 'head'
    tail = 'tail'


def headselectmode(doc):
    doc.selectmode = SelectModes.head
commands.headselectmode = headselectmode


def tailselectmode(doc):
    doc.selectmode = SelectModes.tail
commands.tailselectmode = tailselectmode


def normalselectmode(doc):
    doc.selectmode = SelectModes.normal
commands.normalselectmode = normalselectmode

from . import selectdelimited, selectpattern, selectdelimited, lockrelease, misc
