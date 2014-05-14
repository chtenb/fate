"""
This module contains the key mapping as two dictionaries from chars to functions.
The first one, `actions`, maps chars to actions.
The second one, `actions`, maps chars to ui actions,
i.e. functions which take an UserInterface object.
"""
from . import selectors, operators, actions, uiactions, modes, clipboard, compoundactions
from .session import Session
from . import actions


default = {
    'Ctrl-S': Session.write,
    'Ctrl-Q': Session.quit,
    'Ctrl-O': uiactions.open_session,
    'Ctrl-N': uiactions.next_session,
    'Ctrl-P': uiactions.previous_session,
    'f': uiactions.local_find,
    'F': uiactions.local_find_backwards,
    '/': uiactions.search,
    '*': uiactions.search_current_content,
    'n': uiactions.search_next,
    'N': uiactions.search_previous,
    ':': uiactions.command_mode,
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
    ')': selectors.SelectAround,
    'm': selectors.Join,
    'z': selectors.Complement,
    'A': selectors.SelectEverything,
    'v': selectors.lock_selection,
    'V': selectors.unlock_selection,
    'R': selectors.release_locked_selection,
    'u': actions.undo,
    'U': actions.redo,
    'y': clipboard.copy,
    'Y': clipboard.clear,
    'p': clipboard.paste_after,
    'P': clipboard.paste_after,
    'r': modes.reduce_mode,
    'e': modes.extend_mode,
    'd': operators.delete,
    'i': operators.ChangeBefore,
    'a': operators.ChangeAfter,
    's': operators.ChangeAround,
    'c': operators.ChangeInPlace,
    'Esc': compoundactions.escape,
    'o': compoundactions.OpenLineAfter,
    'O': compoundactions.OpenLineBefore,
    'x': compoundactions.Cut,
    'X': compoundactions.CutChange,
}


def print_keymap(session):
    """Prints the keys with their explanation."""
    def print_key(key, action):
        """Prints single key with docstring."""
        print(key + ': ' + action.__docs__)

    for key, action in session.keymap.items():
        print_key(key, action)

