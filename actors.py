"""Actors are functions that act on a session.
Sequences of actors are again an actor via the actor decorator."""
from .selectors import (NextFullLine, PreviousFullLine, Empty,
                        PreviousChar, NextChar, EmptyBefore,
                        SelectIndent)
from .operators import Insert, Append, ChangeAfter, ChangeBefore, Delete
from .clipboard import copy, paste_before, clear
from .action import compose
from . import modes


def escape(session):
    """Escape"""
    if session.selection_mode != modes.SELECT_MODE:
        modes.select_mode(session)
    else:
        Empty(session)


def undo(session):
    """Undo last action."""
    session.actiontree.undo()


def redo(session):
    """Redo last undo."""
    session.actiontree.redo()

open_line_after = compose(modes.select_mode, PreviousFullLine,
                          SelectIndent, copy,)
                          #next_full_line,
                          #append('\n'),
                          #previous_char, empty_before, paste_before,
                          #clear)#, change_after)
open_line_after.__docs__ = """Open a line after interval."""

open_line_before = compose(modes.select_mode, NextFullLine,
                           SelectIndent, copy,
                           NextFullLine, Insert('\n'),
                           NextChar, EmptyBefore, paste_before,
                           clear, ChangeAfter)
open_line_before.__docs__ = """Open a line before interval."""

cut = compose(copy, Delete)
