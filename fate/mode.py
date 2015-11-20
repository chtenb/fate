"""
A mode takes over the way user input is handled, but only to a certain level.

The current mode decides how input is handled.
So any user input is passed to the processinput method of the current mode.

For example, suppose we are in normal mode.
If the user presses i for insert mode, the i is passed to the normal mode.
The normal mode looks in its keymap and executes the enter_insertmode command.
This command starts the documents insertmode, which puts itself in doc.mode
When insertmode is done, it puts normalmode back in doc.mode and executes its callback,
if provided.

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
"""
from abc import ABC
from logging import error

# We want to be able to adjust modes and their keymaps for individual documents
# Therefore, OnModeInit is fired before OnDocumentInit, so that all functions fired
# by OnDocumentInit can  access the modes.


# TODO: to make mode keymaps configurable in OnDocumentInit, we could either
# make the commands methods of the mode.
# doc.undomode.keymap['w'] = doc.undomode.somecommand
# Do we want to have doc s member, in this case?
#
# Another way is to make them commands.
# doc.undomode.keymap['w'] = somecommand
# A downside of the latter is that the commands have to be imported

class Mode(ABC):

    """Abstract class to make creating new modes more convenient."""
    __name__ = ''

    def __init__(self, doc):
        self.doc = doc
        self.keymap = {doc.cancelkey: self.stop}
        self.allowedcommands = [self.start, self.stop]

    def start(self, doc, callback=None):
        """Must be called to start the mode."""
        if not doc == self.doc:
            raise ValueError(
                'The passed document is not the same as the member document.')

        if doc.mode:
            doc.mode.stop(doc)
        self.callback = callback
        doc.mode = self

    def stop(self, doc):
        """Must be called to stop the mode."""
        if not doc == self.doc:
            raise ValueError(
                'The passed document is not the same as the member document.')

        doc.mode = doc.normalmode
        if self.callback:
            self.callback(doc)

    def __str__(self):
        return self.__name__ or self.__class__.__name__

    def processinput(self, doc, userinput):
        if not doc == self.doc:
            raise ValueError(
                'The passed document is not the same as the member document.')

        # If a direct command is given: execute if we allow it
        if type(userinput) != str:
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
    if type(userinput) == str:
        key = userinput
        if key in keymap:
            command = keymap[key]
        else:
            command = None
    else:
        command = userinput

    return command
