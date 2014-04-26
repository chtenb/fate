"""
This module contains the key mapping as two dictionaries from chars to functions.
The first one, `actions`, maps chars to actions.
The second one, `ui_actions`, maps chars to ui actions,
i.e. functions which take an UserInterface object.
"""
from . import selectors, actors, operators, modes, clipboard
from .session import Session
from . import ui_actions


action_keys = {
    'Ctrl-S': Session.write,
    'Ctrl-Q': Session.quit,
    'Ctrl-O': ui_actions.open_session,
    'Ctrl-N': ui_actions.next_session,
    'Ctrl-P': ui_actions.previous_session,
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
    'f': ui_actions.local_find,
    'F': ui_actions.local_find_backwards,
    '/': ui_actions.search,
    '*': ui_actions.search_current_content,
    'n': ui_actions.search_next,
    'N': ui_actions.search_previous,
}


def init_key_mapping(session):
    session.key_mapping = action_keys.copy()

Session.OnSessionInit.add(init_key_mapping)


def print_key_mapping(session):
    """Prints the keys with their explanation."""
    def print_key(key, action):
        """Prints single key with docstring."""
        print(key + ': ' + action.__docs__)

    for key, action in session.key_mapping.items():
        print_key(key, action)

