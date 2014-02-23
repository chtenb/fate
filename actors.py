"""Actors are functions that act on a session.
Sequences of actors are again an actor via the actor decorator."""
from .selectors import (next_full_line, previous_full_line, empty,
                        previous_char, next_char, empty_before,
                        select_indent)
from .operators import insert, append, change_after, change_before, delete
from .clipboard import copy, paste_before, clear
from .action import compose
from . import modes


def escape(session):
    """Escape"""
    if session.selection_mode != modes.SELECT_MODE:
        modes.select_mode(session)
    else:
        empty(session)


def undo(session):
    """Undo last action."""
    session.actiontree.undo()


def redo(session):
    """Redo last undo."""
    session.actiontree.redo()

open_line_after = compose(modes.select_mode, previous_full_line,
                          select_indent, copy,
                          next_full_line, append('\n'),
                          previous_char, empty_before, paste_before,
                          clear)
open_line_after.__docs__ = """Open a line after interval."""

open_line_before = compose(modes.select_mode, next_full_line,
                           select_indent, copy,
                           next_full_line, insert('\n'),
                           next_char, empty_before, paste_before,
                           clear)
open_line_before.__docs__ = """Open a line before interval."""

cut = compose(copy, delete)
