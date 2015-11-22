import random
from re import escape
from ..userinterface import UserInterfaceAPI
from ..commandmode import publics
from .. import commands
from .. import normalmode  # Dependency
from ..document import Document
from ..filecommands import open_file, quit_document, force_quit, quit_all
from ..errorchecking import checkerrors
from ..formatting import formattext

# All keys that can be entered by the user simulator
key_space = list(
    """
    1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM
    `-=[]\\;',./~_+{}|:"<>?
    !@#$%&*()
    \n\t\b
    """
) + 30 * [Document.cancelkey] + ['up', 'down', 'left', 'right']

command_space = publics(commands)
forbidden_commands = [open_file, quit_document, force_quit, quit_all, formattext, checkerrors]
for c in forbidden_commands:
    command_space.pop(c.__name__)

compound_input_space = list(command_space.values()) + key_space
# Sorting is needed to be able to reproduce a seeded random test case
compound_input_space.sort(key=str)


class RandomizedUserSimulator(UserInterfaceAPI):

    """UserInterface which simulates some random behaviour for testing purposes."""

    def __init__(self, doc):
        UserInterfaceAPI.__init__(self, doc)
        self.nextkey = None
        self.offset = 0

    @property
    def viewport_size(self):
        """Get viewport size."""
        return (100, 500)

    @property
    def viewport_offset(self):
        """Get and set viewport offset."""
        return self.offset

    @viewport_offset.setter
    def viewport_offset(self, value):
        """Get and set viewport offset."""
        assert isinstance(value, int)
        self.offset = value

    def quit(self, doc):
        assert doc is self.doc

    def _getuserinput(self):
        if self.nextkey:
            result = self.nextkey
            self.nextkey = None
        else:
            result = self.newinput()
        return result

    def peekinput(self):
        if not self.nextkey:
            self.nextkey = self.newinput()
        return self.nextkey

    def newinput(self):
        # With a certain chance give arbitrary input instead of looking at the keymap
        if random.randint(0, 1) == 0:
            input_space = compound_input_space
        else:
            # Try to construct a meaningful input space w.r.t. the mode
            mode = self.doc.mode
            # Save the input_space for each mode, to speed things up
            if not hasattr(mode, 'input_space'):
                input_space = [Document.cancelkey]
                input_space = mode.allowedcommands
                input_space.extend(mode.keymap.values())

                input_space = [x for x in input_space if not x in forbidden_commands]
                input_space.sort(key=str)
                mode.input_space = input_space
            else:
                input_space = mode.input_space

        #print('Inputspace = ' + str(input_space))
        return random.choice(input_space)

    def prompt(self, prompt_string='>'):
        length = random.randint(1, 10)
        # Generate random string
        randomstring = ''.join(self.getkey() for _ in range(length))
        # Escape string to ensure a valid regex
        return escape(randomstring)

    def notify(self, message):
        pass

    def activate(self):
        pass

    def touch(self):
        pass
