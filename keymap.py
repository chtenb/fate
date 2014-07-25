"""
This module contains the key mapping as two dictionaries from chars to functions.
The first one, `actions`, maps chars to actions.
The second one, `actions`, maps chars to ui actions,
i.e. functions which take an UserInterface object.
"""
from . import actions
from .session import Session
from . import actions


default = {
    'Ctrl-S': Session.write,
    'Ctrl-Q': Session.quit,
    'Ctrl-O': actions.open_session,
    'Ctrl-N': actions.next_session,
    'Ctrl-P': actions.previous_session,
    'f': actions.local_find,
    'F': actions.local_find_backwards,
    '/': actions.search,
    '*': actions.search_current_content,
    'n': actions.search_next,
    'N': actions.search_previous,
    ':': actions.command_mode,
    'j': actions.NextLine,
    'k': actions.PreviousLine,
    'J': actions.NextFullLine,
    'K': actions.PreviousFullLine,
    'l': actions.NextChar,
    'h': actions.PreviousChar,
    'w': actions.NextWord,
    'b': actions.PreviousWord,
    'W': actions.NextClass,
    'B': actions.PreviousClass,
    '}': actions.NextParagraph,
    '{': actions.PreviousParagraph,
    ')': actions.SelectAround,
    ']': actions.SelectAroundChar,
    'm': actions.Join,
    'z': actions.Complement,
    'A': actions.SelectEverything,
    'I': actions.SelectIndent,
    'v': actions.lock,
    'V': actions.unlock,
    'R': actions.release,
    'u': actions.undo,
    'U': actions.redo,
    'Ctrl-U': actions.undo_mode,
    'y': actions.copy,
    'Y': actions.clear,
    'p': actions.paste_after,
    'P': actions.paste_after,
    'r': actions.reduce_mode,
    'e': actions.extend_mode,
    'd': actions.delete,
    'i': actions.ChangeBefore,
    'a': actions.ChangeAfter,
    's': actions.ChangeAround,
    'c': actions.ChangeInPlace,
    'Esc': actions.escape,
    'o': actions.OpenLineAfter,
    'O': actions.OpenLineBefore,
    'x': actions.Cut,
    'X': actions.CutChange,
}


def print_keymap(session):
    """Prints the keys with their explanation."""
    def print_key(key, action):
        """Prints single key with docstring."""
        print(key + ': ' + action.__docs__)

    for key, action in session.keymap.items():
        print_key(key, action)

