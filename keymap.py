"""
This module contains the key mapping as two dictionaries from chars to functions.
The first one, `actions`, maps chars to actions.
The second one, `uiactions`, maps chars to ui actions,
i.e. functions which take an UserInterface object.
"""
from . import selectors, actors, operators, modes, clipboard
from .session import Session
from . import uiactions


default = {
    'Ctrl-S': Session.write,
    'Ctrl-Q': Session.quit,
    'Ctrl-O': uiactions.open_session,
    'Ctrl-N': uiactions.next_session,
    'Ctrl-P': uiactions.previous_session,
    'j': selectors.NextLine,
    'k': selectors.PreviousLine,
    'J': selectors.NextFullLine,
    'K': selectors.PreviousFullLine,
    'l': selectors.NextChar,
    'h': selectors.PreviousChar,
    'w': selectors.NextWord,
    'b': selectors.PreviousWord,
    '}': selectors.NextParagraph,
    '{': selectors.PreviousParagraph,
    'm': selectors.Join,
    'z': selectors.Complement,
    'A': selectors.SelectEverything,
    'u': actors.undo,
    'U': actors.redo,
    'y': clipboard.copy,
    'Y': clipboard.clear,
    'p': clipboard.paste_after,
    'P': clipboard.paste_after,
    'x': actors.Cut,
    'X': actors.CutChange,
    'Esc': actors.escape,
    'd': operators.delete,
    'r': modes.reduce_mode,
    'e': modes.extend_mode,
    'i': operators.ChangeBefore,
    'a': operators.ChangeAfter,
    's': operators.ChangeAround,
    'c': operators.ChangeInPlace,
    'o': actors.OpenLineAfter,
    'O': actors.OpenLineBefore,
    'f': uiactions.local_find,
    'F': uiactions.local_find_backwards,
    '/': uiactions.search,
    '*': uiactions.search_current_content,
    'n': uiactions.search_next,
    'N': uiactions.search_previous,
}


def print_keymap(session):
    """Prints the keys with their explanation."""
    def print_key(key, action):
        """Prints single key with docstring."""
        print(key + ': ' + action.__docs__)

    for key, action in session.keymap.items():
        print_key(key, action)

