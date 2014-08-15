"""
This module contains the key mapping as two dictionaries from chars to functions.
The first one, `commands`, maps chars to commands.
The second one, `commands`, maps chars to ui commands,
i.e. functions which take an UserInterface object.
"""
from . import commands
from .document import Document
from . import commands


default = {
    'Ctrl-S': Document.write,
    'Ctrl-Q': commands.quit_document,
    'Ctrl-X': commands.force_quit,
    'Ctrl-O': commands.open_document,
    'Ctrl-N': commands.next_document,
    'Ctrl-P': commands.previous_document,
    'f': commands.local_find,
    'F': commands.local_find_backwards,
    '/': commands.search,
    '*': commands.search_current_content,
    'n': commands.search_next,
    'N': commands.search_previous,
    ':': commands.command_mode,
    'j': commands.NextLine,
    'k': commands.PreviousLine,
    'J': commands.NextFullLine,
    'K': commands.PreviousFullLine,
    'l': commands.NextChar,
    'h': commands.PreviousChar,
    'w': commands.NextWord,
    'b': commands.PreviousWord,
    'W': commands.NextClass,
    'B': commands.PreviousClass,
    '}': commands.NextParagraph,
    '{': commands.PreviousParagraph,
    ')': commands.SelectAround,
    ']': commands.SelectAroundChar,
    'm': commands.Join,
    'z': commands.Complement,
    'A': commands.SelectEverything,
    'I': commands.SelectIndent,
    'v': commands.lock,
    'V': commands.unlock,
    'R': commands.release,
    'u': commands.undo,
    'U': commands.redo,
    'Ctrl-U': commands.undo_mode,
    'y': commands.copy,
    'Y': commands.clear,
    'p': commands.paste_after,
    'P': commands.paste_after,
    'r': commands.reduce_mode,
    'e': commands.extend_mode,
    'd': commands.delete,
    'i': commands.ChangeBefore,
    'a': commands.ChangeAfter,
    's': commands.ChangeAround,
    'c': commands.ChangeInPlace,
    'Esc': commands.escape,
    'o': commands.OpenLineAfter,
    'O': commands.OpenLineBefore,
    'x': commands.Cut,
    'X': commands.CutChange,
    '.': commands.repeat,
    '~': commands.uppercase,
    '`': commands.lowercase,
}


def print_keymap(document):
    """Prints the keys with their explanation."""
    def print_key(key, command):
        """Prints single key with docstring."""
        print(key + ': ' + command.__docs__)

    for key, command in document.keymap.items():
        print_key(key, command)

