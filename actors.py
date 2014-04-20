"""Actors are functions that act on a session.
Sequences of actors are again an actor via the actor decorator."""
from .selectors import (NextFullLine, PreviousFullLine, Empty,
                        PreviousChar, NextChar, EmptyBefore,
                        SelectIndent)
from .operators import Insert, Append, ChangeAfter, delete, ChangeInPlace
from .clipboard import copy, PasteBefore, clear
from .action import Compose
from . import modes
from functools import partial

# TODO: decide upon naming convention for actions
# Actions can be function, regular objects or classes
# Let's say
# Action constructors: CamelCase
# Actions: camelcase or camel_case

def escape(session):
    """Escape"""
    if session.selection_mode != modes.SELECT_MODE:
        modes.select_mode(session)
    else:
        Empty(session)


def undo(session):
    """Undo last action."""
    session.undotree.undo()


def redo(session):
    """Redo last undo."""
    session.undotree.redo()

OpenLineAfter = Compose(modes.select_mode, PreviousFullLine,
                          SelectIndent, copy,
                          NextFullLine,
                          partial(Append, '\n'),
                          PreviousChar, EmptyBefore, PasteBefore,
                          clear, ChangeAfter)
OpenLineAfter.__docs__ = """Open a line after interval."""
OpenLineAfter.__name__ = 'OpenLineAfter'

OpenLineBefore = Compose(modes.select_mode, NextFullLine,
                           SelectIndent, copy,
                           NextFullLine, partial(Insert, '\n'),
                           NextChar, EmptyBefore, PasteBefore,
                           clear, ChangeAfter)
OpenLineBefore.__docs__ = """Open a line before interval."""
OpenLineBefore.__name__ = 'OpenLineBefore'

cut = Compose(copy, delete)
cut.__docs__ = 'Copy and delete selected text.'
cut.__name__ = 'cut'

CutChange = Compose(copy, ChangeInPlace, Insert('Hello world! '))
CutChange.__docs__ = 'Copy and change selected text.'
CutChange.__name__ = 'CutChange'
