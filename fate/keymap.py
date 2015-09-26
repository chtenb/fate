"""
This module contains the key mapping as two dictionaries from keys to functions.
The first one, `commands`, maps keys to commands.
The second one, `commands`, maps keys to ui commands,
i.e. functions which take an UserInterface object.
"""
from . import commands
from .document import Document

Document.cancelkey = 'esc'  # Esc is now remapped to Cancel
default = {
    # In normalmode the cancel key switches to normal select mode or empties thselection
    'esc': commands.escape,
    'ctrl-s': commands.save,
    'ctrl-l': commands.load,
    'ctrl-q': commands.quit_document,
    'ctrl-x': commands.force_quit,
    'ctrl-o': commands.open_document,
    'ctrl-n': commands.next_document,
    'ctrl-p': commands.previous_document,
    'f3': commands.formattext,
    'f4': commands.checkerrors,
    'f5': commands.errormode,
    'f': commands.local_find,
    'F': commands.local_find_backward,
    '/': commands.search,
    '*': commands.search_current_content,
    'n': commands.search_next,
    'N': commands.search_previous,
    ':': commands.commandmode,
    'j': commands.movedown,
    'k': commands.moveup,
    'J': commands.selectnextfullline,
    'K': commands.selectpreviousfullline,
    'l': commands.selectnextchar,
    'h': commands.selectpreviouschar,
    'g': commands.selectline,
    'G': commands.selectfullline,
    'w': commands.selectnextword,
    'b': commands.selectpreviousword,
    'W': commands.selectnextclass,
    'B': commands.selectpreviousclass,
    '}': commands.selectnextparagraph,
    '{': commands.selectpreviousparagraph,
    ')': commands.select_next_delimiting,
    '(': commands.select_previous_delimiting,
    ']': commands.select_next_delimiting_char,
    '[': commands.select_previous_delimiting_char,
    'm': commands.join,
    'z': commands.emptybefore,
    'ctrl-a': commands.selectall,
    'I': commands.selectindent,
    'v': commands.lock,
    'V': commands.unlock,
    'R': commands.release,
    'u': commands.undo,
    'U': commands.redo,
    'ctrl-u': commands.undomode,
    'y': commands.copy,
    'Y': commands.clear,
    'p': commands.paste_after,
    'P': commands.paste_after,
    'r': commands.headselectmode,
    'e': commands.tailselectmode,
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
    'ctrl-f': commands.pagedown,
    'ctrl-b': commands.pageup,
}


def print_keymap(document):
    """Prints the keys with their explanation."""
    def print_key(key, command):
        """Prints single key with docstring."""
        print(key + ': ' + command.__docs__)

    for key, command in document.keymap.items():
        print_key(key, command)
