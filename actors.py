"""Actors are functions that act on a session.
Sequences of actors are again an actor via the actor decorator."""
from .selectors import (NextFullLine, PreviousFullLine, Empty,
                        PreviousChar, NextChar, EmptyBefore,
                        SelectIndent)
from .operators import Insert, Append, ChangeAfter, delete, ChangeInPlace
from .clipboard import copy, paste_before, clear
from .action import Compose, Interactive
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


class Pause(Interactive):

    """Don't do anything, until we proceed."""

    def __init__(self, session):
        pass

    def interact(self, session, string):
        pass

OpenLineAfter = Compose(modes.select_mode, PreviousFullLine, SelectIndent, copy,
                        NextFullLine, Append('\n'), PreviousChar, EmptyBefore,
                        paste_before, clear, ChangeAfter, name='OpenLineAfter',
                        docs='Open a line after interval')

OpenLineBefore = Compose(modes.select_mode, NextFullLine, SelectIndent, copy,
                         NextFullLine, Insert('\n'), NextChar, EmptyBefore,
                         paste_before, clear, ChangeAfter, name='OpenLineBefore',
                         docs='Open a line before interval')

Cut = Compose(copy, delete, name='Cut', docs='Copy and delete selected text.')

CutChange = Compose(copy, ChangeInPlace, Insert('Hello world! '),
                    name='CutChange', docs='Copy and change selected text.')
