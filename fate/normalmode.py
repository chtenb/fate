from .mode import Mode, input_to_command
from .document import Document
from . import pointer
from . import commands

from copy import copy
import logging


def print_keymap(document):
    """Prints the keys with their explanation."""
    def print_key(key, command):
        """Prints single key with docstring."""
        print(key + ': ' + command.__docs__)

    for key, command in document.keymap.items():
        print_key(key, command)

Document.cancelkey = 'esc'  # Esc is now remapped to cancelkey

default_keymap = {
    # In normalmode the cancel key switches to normal select mode or empties thselection
    'esc': commands.escape,
    'ctrl-s': commands.save,
    'ctrl-l': commands.load,
    'ctrl-q': commands.quit_document,
    'ctrl-x': commands.force_quit,
    'ctrl-o': commands.open_file,
    'ctrl-n': commands.next_document,
    'ctrl-p': commands.previous_document,
    'f3': commands.formattext,
    'f4': commands.checkerrors,
    'f5': commands.start_errormode,
    'f': commands.local_find,
    'F': commands.local_find_backward,
    '/': commands.search,
    '*': commands.search_current_content,
    'n': commands.search_next,
    'N': commands.search_previous,
    ':': commands.commandmode,
    'j': commands.movedown,
    'k': commands.moveup,
    'down': commands.selectnextline,
    'up': commands.selectpreviousline,
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
    'Z': commands.emptyafter,
    'ctrl-a': commands.selectall,
    'I': commands.selectindent,
    'v': commands.lock,
    'V': commands.unlock,
    'R': commands.release,
    'u': commands.undo,
    'U': commands.redo,
    'ctrl-u': commands.start_undomode,
    'y': commands.copy,
    'Y': commands.clear,
    'p': commands.paste_after,
    'P': commands.paste_after,
    'r': commands.headselectmode,
    'e': commands.tailselectmode,
    'd': commands.delete,
    'i': commands.changebefore,
    'a': commands.changeafter,
    's': commands.start_changearound,
    'c': commands.start_changeinplace,
    'o': commands.openlineafter,
    'O': commands.openlinebefore,
    'x': commands.cut,
    'X': commands.cutchange,
    '.': commands.repeat,
    '~': commands.uppercase,
    '`': commands.lowercase,
    'ctrl-f': commands.pagedown,
    'ctrl-b': commands.pageup,
}



class NormalMode(Mode):

    """Docstring for NormalMode. """

    def __init__(self, doc):
        Mode.__init__(self, doc)
        self.keymap = copy(default_keymap)

    def start(self, doc, callback=None):
        """Must be called to start the mode."""
        if not doc == self.doc:
            raise ValueError(
                'The passed document is not the same as the member document.')
        if callback:
            raise ValueError('normalmode does not take a callback.')

        if doc.mode:
            doc.mode.stop(doc)
        doc.mode = self

    def stop(self, doc):
        pass

    def processinput(self, doc, userinput):
        if isinstance(userinput, pointer.PointerInput):
            self.process_pointerinput(userinput)
        else:
            command = input_to_command(self.doc, userinput)
            if command:
                command(self.doc)

    def process_pointerinput(self, userinput):
        assert isinstance(userinput, pointer.PointerInput)

        if userinput.length:
            logging.debug('You sweeped from position {} till {}'
                          .format(userinput.pos, userinput.pos + userinput.length))
        else:
            logging.debug('You clicked at position ' + str(userinput.pos))


def init_normalmode(doc):
    doc.modes.normalmode = NormalMode(doc)
Document.OnModeInit.add(init_normalmode)


def start_normalmode(doc, callback=None):
    doc.modes.normalmode.start(doc, callback)
commands.start_normalmode = start_normalmode

