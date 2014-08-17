"""
This module contains the key mapping as two dictionaries from keys to functions.
The first one, `commands`, maps keys to commands.
The second one, `commands`, maps keys to ui commands,
i.e. functions which take an UserInterface object.
"""
from . import commands
from .document import Document

Document.cancelkey = 'Esc' # Esc is now remapped to Cancel

default = {
    'Cancel': commands.empty, # In normalmode the cancel key empties selection
    'Ctrl-s': commands.save,
    'Ctrl-q': commands.quit_document,
    'Ctrl-x': commands.force_quit,
    'Ctrl-o': commands.open_document,
    'Ctrl-n': commands.next_document,
    'Ctrl-p': commands.previous_document,
    'f': commands.local_find,
    'F': commands.local_find_backwards,
    '/': commands.search,
    '*': commands.search_current_content,
    'n': commands.search_next,
    'N': commands.search_previous,
    ':': commands.commandmode,
    'j': commands.nextline,
    'k': commands.previousline,
    'J': commands.nextfullline,
    'K': commands.previousfullline,
    'l': commands.nextchar,
    'h': commands.previouschar,
    'w': commands.nextword,
    'b': commands.previousword,
    'W': commands.nextclass,
    'B': commands.previousclass,
    '}': commands.nextparagraph,
    '{': commands.previousparagraph,
    ')': commands.selectaround,
    ']': commands.selectaround_char,
    'm': commands.join,
    'z': commands.complement,
    'A': commands.selectall,
    'I': commands.selectindent,
    'v': commands.lock,
    'V': commands.unlock,
    'R': commands.release,
    'u': commands.undo,
    'U': commands.redo,
    'Ctrl-u': commands.undomode,
    'y': commands.copy,
    'Y': commands.clear,
    'p': commands.paste_after,
    'P': commands.paste_after,
    'r': commands.reducemode,
    'e': commands.extendmode,
    'd': commands.delete,
    'i': commands.ChangeBefore,
    'a': commands.ChangeAfter,
    's': commands.ChangeAround,
    'c': commands.ChangeInPlace,
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

