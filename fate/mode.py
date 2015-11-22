"""
A mode takes over the way user input is handled, but only to a certain level.

The current mode decides how input is handled.
So any user input is passed to the processinput method of the current mode.

Sometimes you want to be able to continue with something after the mode has finished.
Therefore modes should be able to take a callback function.
This way modes can be used inside other commands.
However, say we want to go into undo mode and change the point in history and go back.
Not necessary, just execute the commands for changing the point in history.
So switching modes inside another command is not always the way to go,
since a mode only affects how input is handled.

It seems that using callbacks for finishing a mode is the only option.
This way we don't need nested modes, so we can keep using them like commands.
How do we implement Compose then?
Compose will not be a mode. It just fires modes passing itself as a callback.
Disadvantage: the toplevel composition isn't visible.
The only reference existing is through the callback.


We want to be able to adjust modes and their keymaps for individual documents
Therefore, OnModeInit is fired before OnDocumentInit, so that all functions fired
by OnDocumentInit can access the modes.
By convention, the modes should be stored as members of the document, like
doc.normalmode.

To make mode keymaps configurable in OnDocumentInit, we could either
make the commands methods of the mode.
doc.undomode.keymap['w'] = doc.undomode.somecommand
Do we want to have doc s member, in this case?

Another way is to make them commands.
doc.undomode.keymap['w'] = somecommand
A downside of the latter is that the commands have to be imported

There is no convention yet on how to do this.
"""
from abc import ABC
from logging import error

class Mode(ABC):

    """Abstract class to make creating new modes more convenient."""
    __name__ = ''

    def __init__(self, doc):
        self.doc = doc
        self.keymap = {doc.cancelkey: self.stop}
        self.allowedcommands = [self.start, self.stop]

    def __call__(self, doc, callback=None):
        """Alternative way to call start() to be able to use a mode as a command."""
        self.start(doc, callback)

    def start(self, doc, callback=None):
        """
        Must be called to start the mode.
        If there is another mode pending, stop it.
        Then put self in the mode field of the document.
        """
        if not doc == self.doc:
            raise ValueError(
                'The passed document is not the same as the member document.')

        if doc.mode:
            doc.mode.stop(doc)
        self.callback = callback
        doc.mode = self

    def stop(self, doc):
        """
        Must be called to stop the mode.
        Put the documents normalmode in the mode field and execute possible callback.
        """
        if not doc == self.doc:
            raise ValueError(
                'The passed document is not the same as the member document.')

        doc.mode = doc.normalmode
        if self.callback:
            self.callback(doc)

    def __str__(self):
        return self.__name__ or self.__class__.__name__

    def processinput(self, doc, userinput):
        """
        Tries to process the given input.
        Returns True if succeeded, False otherwise.
        """
        if not doc == self.doc:
            raise ValueError(
                'The passed document is not the same as the member document.')

        # If a direct command is given: execute if we allow it
        if not isinstance(userinput, str):
            if userinput in self.allowedcommands:
                userinput(doc)
                return True
            else:
                return False

        # If a key in our keymap is given: execute it
        if userinput in self.keymap:
            command = self.keymap[userinput]
            command(doc)
            return True

        # If a key in doc.keymap is given: execute if we allow it
        if userinput in doc.normalmode.keymap:
            command = doc.normalmode.keymap[userinput]
            if command in self.allowedcommands:
                command(doc)
                return True
            else:
                return False

        return False


def input_to_command(doc, userinput, keymap=None):
    """
    Convert given userinput to a command.
    If keymap is not given, document.keymap is used.
    Returns None if userinput is a key but is not in keymap.
    """
    keymap = keymap or doc.mode.keymap
    if isinstance(userinput, str):
        key = userinput
        if key in keymap:
            command = keymap[key]
        else:
            command = None
    else:
        command = userinput

    return command
