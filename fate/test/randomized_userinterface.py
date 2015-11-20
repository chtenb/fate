import random
from re import escape
from ..userinterface import UserInterfaceAPI
from ..commandmode import publics
from .. import commands
from .. import normalmode # Dependency
from ..document import Document

# All keys that can be entered by the user simulator
# Esc is included more often, to keep the insertions relatively small
key_space = list(
    """
    1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM
    `-=[]\\;',./~_+{}|:"<>?
    !@#$%&*()
    \n\t\b
    """
) + 30 * [Document.cancelkey] + ['up', 'down', 'left', 'right']

command_dict = publics(commands)
forbidden_command_names = ['open_document', 'quit_document', 'force_quit', 'quit_all',
                           'formattext', 'checkerrors']
forbidden_commands = [command_dict[name] for name in forbidden_command_names]
for name in forbidden_command_names:
    command_dict.pop(name)
command_names = list(command_dict.keys())
command_values = list(command_dict.values())
# Sorting is needed to be able to reproduce a seeded random test case
command_names.sort()

compound_input_space = command_values + key_space


class RandomizedUserSimulator(UserInterfaceAPI):

    """UserInterface which simulates some random behaviour for testing purposes."""

    def __init__(self, doc):
        UserInterfaceAPI.__init__(self, doc)
        self.nextkey = None
        self.offset = 0

    @property
    def viewport_size(self):
        """Get viewport size."""
        return (500, 500)

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
            nextkey = self.nextkey
            self.nextkey = None
        else:
            nextkey = self.newinput()
        return nextkey

    def peekinput(self):
        if not self.nextkey:
            self.nextkey = self.newinput()
        return self.nextkey

    def newinput(self):
        if not self.doc.mode:
            command_name = random.choice(command_names)
            return command_dict[command_name]

        # If we are in a certain mode we try to construct a meaningful input space
        mode = self.doc.mode
        input_space = ['Cancel']
        input_space.extend(
            [c for c in mode.allowedcommands if not c in forbidden_commands])

        if mode.keymap:
            input_space.extend(mode.keymap.values())
        else:
            input_space.extend(key_space)

        if not input_space:
            input_space = compound_input_space

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
