"""
Mode are persistent commands, i.e. commands that take additional user input
to complete, and that may be interrupted by other commands (such as switching
to another document) without being cancelled.
Effectively, a mode takes over the way user input is handled, but only to a certain level.

Sometimes you want to be able to continue with something after the mode has finished.
Therefore modes should be able to take a callback function.
This way modes can be used inside other commands.



IDEA:
The current mode decides how input is handled.
So any user input is passed to the processinput method of the current mode.

For example, suppose we are in normal mode.
If the user presses i for insert mode, the i is passed to the normal mode.
The normal mode looks in its keymap and decides that we should enter insert mode.
The normal mode then creates an insert mode object, and stores it in his submode field.
To do this, it needs to perform an isinstance check.
Any input that follows will still be passed to the normal mode,
but normal mode passes it on to its submode, in this case the insert mode.
If the insert mode wants to stop at some point, it could notify the
normal mode by setting a boolean or by calling a callback function for instance.
PROBLEM: a mode is not a command anymore

What if we are in some mode and inside another command we want to go into another mode?
Say we want to go into undo mode and change the point in history and go back.
Not necessary, just execute the commands for changing the point in history.
So switching modes inside another command doesn't make sense,
since a mode only affects how input is handled.

It seems that using callbacks for finishing a mode is the only option.
This way we don't need nested modes, so we can keep using them like commands.
How do we implement Compose then?
Compose will not be a mode. It just fires modes passing itself as a callback.
Disadvantage: the toplevel composition isn't visible.
The only reference existing is through the callback.

REMARK:
A mode is thus not necessarily stateful.
How can we modify a mode keymap for a single document?
"""


class Mode:

    """Abstract class to make creating new modes more convenient."""

    def __init__(self, document, callback):
        self.keymap = {}
        self.allowedcommands = []
        self.callback = callback

    def start(self, document):
        """Must be called to start the mode."""
        assert document.mode == None
        document.mode = self

    def stop(self, document):
        """Must be called to stop the mode."""
        document.mode = None
        if self.callback:
            self.callback(document)

    def __str__(self):
        try:
            return self.__name__
        except AttributeError:
            return self.__class__.__name__

    def processinput(self, document, userinput):
        raise NotImplementedError('An abstract method is not callable.')


def input_to_command(document, userinput, keymap=None):
    """
    Convert given userinput to a command.
    If keymap is not given, document.keymap is used.
    Returns None if userinput is a key but is not in keymap.
    """
    keymap = keymap or document.keymap
    if type(userinput) == str:
        key = userinput
        if key in keymap:
            command = keymap[key]
        else:
            command = None
    else:
        command = userinput

    return command


def normalmode(document, userinput):
    """Process input as if we were in normal mode."""
    command = input_to_command(document, userinput)
    command(document)
