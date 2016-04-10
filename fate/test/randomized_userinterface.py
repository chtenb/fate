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

# TODO: to remove the requirement of complete determinism of fate w.r.t. a randomizer seed
# we could generate a large enough pool of random numbers on beforehand based on a
# given/generated seed, and feed this to the random number generator when choosing the commands
# during testing.

# All keys that can be entered by the user simulator
key_list = list(
    """
    1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM
    `-=[]\\;',./~_+{}|:"<>?
    !@#$%&*()
    \n\t\b
    """
) + 30 * [Document.cancelkey] + ['up', 'down', 'left', 'right']

command_dict = publics(commands)
forbidden_commands = [open_file, quit_document, force_quit, quit_all, formattext,
                      checkerrors]
for c in forbidden_commands:
    command_dict.pop(c.__name__)

command_list = list(command_dict.values())

# Sorting is needed to be able to reproduce a seeded random test case
# We have to use the name for sorting, to make sure the sorting is unique
# Verify that the sorting will be unique
command_space_identifiers = {x.__name__ for x in command_list}
assert len(command_space_identifiers) == len(command_list)


def command_name(command):
    return command.__name__

command_list.sort(key=command_name)

compound_input_space = command_list + key_list


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
                command_space = [c for c in mode.allowedcommands
                                 if not c in forbidden_commands]

                # Verify that the sorting will be unique
                command_space_identifiers = {command_name(x) for x in command_space}
                assert len(command_space_identifiers) == len(command_space)

                command_space.sort(key=command_name)

                key_space = [Document.cancelkey]
                key_space += [k for k in mode.keymap.keys()
                              if not mode.keymap[k] in forbidden_commands]

                input_space = command_space + key_space
                mode.input_space = input_space
            else:
                input_space = mode.input_space

        # print('Inputspace = ' + str(input_space))
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
