"""
This module contains the key mapping as two dictionaries from chars to functions.
The first one, `actions`, maps chars to actions.
The second one, `actions`, maps chars to ui actions,
i.e. functions which take an UserInterface object.
"""
from . import selectors, operators, actions, uiactions, actors, modes, clipboard
from .session import Session
from . import actions


default = {
    'Ctrl-S': Session.write,
    'Ctrl-Q': Session.quit,
    'Ctrl-O': actions.open_session,
    'Ctrl-N': actions.next_session,
    'Ctrl-P': actions.previous_session,
    'j': actions.NextLine,
    'k': actions.PreviousLine,
    'J': actions.NextFullLine,
    'K': actions.PreviousFullLine,
    'l': actions.NextChar,
    'h': actions.PreviousChar,
    'w': actions.NextWord,
    'b': actions.PreviousWord,
    '}': actions.NextParagraph,
    '{': actions.PreviousParagraph,
    'm': actions.Join,
    'z': actions.Complement,
    'A': actions.SelectEverything,
    'u': actions.undo,
    'U': actions.redo,
    'y': clipboard.copy,
    'Y': clipboard.clear,
    'p': clipboard.paste_after,
    'P': clipboard.paste_after,
    'x': actions.Cut,
    'X': actions.CutChange,
    'Esc': actions.escape,
    'd': actions.delete,
    'r': modes.reduce_mode,
    'e': modes.extend_mode,
    'i': actions.ChangeBefore,
    'a': actions.ChangeAfter,
    's': actions.ChangeAround,
    'c': actions.ChangeInPlace,
    'o': actions.OpenLineAfter,
    'O': actions.OpenLineBefore,
    'f': actions.local_find,
    'F': actions.local_find_backwards,
    '/': actions.search,
    '*': actions.search_current_content,
    'n': actions.search_next,
    'N': actions.search_previous,
    ':': actions.command_mode,
}


def print_keymap(session):
    """Prints the keys with their explanation."""
    def print_key(key, action):
        """Prints single key with docstring."""
        print(key + ': ' + action.__docs__)

    for key, action in session.keymap.items():
        print_key(key, action)

