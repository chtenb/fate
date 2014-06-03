"""This module contains more complex actions that are built of other primitive actions."""

from . import modes
from . import actions
from .actiontools import Compose
from .selectors import (Empty, EmptyBefore, PreviousFullLine,
                        SelectIndent, NextFullLine, NextChar, PreviousChar)
from .operators import (Append, ChangeAfter, Insert, ChangeInPlace, delete)
from .clipboard import copy, clear, paste_before


def escape(session):
    """Escape"""
    if session.selection_mode != modes.SELECT_MODE:
        modes.select_mode(session)
    else:
        Empty(session)
actions.escape = escape

OpenLineAfter = Compose(modes.select_mode, PreviousFullLine, SelectIndent, copy,
                        NextFullLine, Append('\n'), PreviousChar, EmptyBefore,
                        paste_before, clear, ChangeAfter, name='OpenLineAfter',
                        docs='Open a line after interval')
actions.OpenLineAfter = OpenLineAfter

OpenLineBefore = Compose(modes.select_mode, NextFullLine, SelectIndent, copy,
                         NextFullLine, Insert('\n'), NextChar, EmptyBefore,
                         paste_before, clear, ChangeAfter, name='OpenLineBefore',
                         docs='Open a line before interval')
actions.OpenLineBefore = OpenLineBefore

Cut = Compose(copy, delete, name='Cut', docs='Copy and delete selected text.')
actions.Cut = Cut

CutChange = Compose(copy, ChangeInPlace, Insert('Hello world! '),
                    name='CutChange', docs='Copy and change selected text.')
actions.CutChange = CutChange
