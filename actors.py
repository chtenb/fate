"""Actors are functions that act on a session.
Sequences of actors are again an actor via the actor decorator."""
from .selectors import (NextFullLine, PreviousFullLine, Empty,
                        PreviousChar, NextChar, EmptyBefore,
                        SelectIndent)
from .operators import Insert, Append, ChangeAfter, Delete
from .clipboard import copy, PasteBefore, clear
from .action import compose
from . import modes
from functools import partial

# Actions

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

# Actors

OpenLineAfter = compose(modes.select_mode, PreviousFullLine,
                          SelectIndent, copy,
                          NextFullLine,
                          partial(Append, '\n'),
                          PreviousChar, EmptyBefore, PasteBefore,
                          clear, ChangeAfter)
#OpenLineAfter.__docs__ = """Open a line after interval."""

OpenLineBefore = compose(modes.select_mode, NextFullLine,
                           SelectIndent, copy,
                           NextFullLine, partial(Insert, '\n'),
                           NextChar, EmptyBefore, PasteBefore,
                           clear, ChangeAfter)
#OpenLineBefore.__docs__ = """Open a line before interval."""

cut = compose(copy, Delete)
