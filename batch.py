"""
Contains functions for using fate as batch processing text tool.
"""
import re
from logging import debug, info, critical
from typing import List

from fate import document, run
from fate.document import documentlist, Document
from fate.test.fake_userinterface import FakeUserInterface

from fate.filecommands import save, force_quit


class ParseError(Exception):

    def __init__(self, inputstring: str, verificationstring: str, first_difference: int):
        Exception.__init__(self)
        self.inputstring = inputstring
        self.verificationstring = verificationstring
        self.first_difference = first_difference

    def __str__(self):
        return 'Parse error:\n{}\n{}\n{}'.format(self.inputstring,
                                                 self.verificationstring,
                                                 ' ' * self.first_difference + '^')


def keys_to_bytestring(keys: List[str]) -> bytes:
    result = []
    for key in keys:
        assert len(key) > 0
        if len(key) == 1:
            if key == '<':
                result.append('\\')
            result.append(key)
        else:
            result.append('<{}>'.format(key))

    result = ''.join(result)
    result = repr(result)[1:-1] # hack to encode newlines in escaped notation
    return result


def batch(filenames: list, inputstring: bytes):
    """
    Some keys consist of more than one character. We need a way to group these together.
    Let's use <...> for that, just like Vim.
    """
    # Create all documents
    if not filenames:
        info('No filenames given')
        return

    Document.create_userinterface = FakeUserInterface

    # Interpret things like new line characters
    # (solution from SO I don't understand)
    inputbytes = bytes(inputstring, "utf-8")
    processed_string = inputbytes.decode("unicode_escape")

    # Parse input string into a list of keys
    key_regex = re.compile(r'(?!<\\)<\w+>|\\<|.', re.DOTALL)
    keys = key_regex.findall(processed_string)

    # Scrap multicharacter key delimiters
    keys = [key if len(key) == 1 else key[1:-1] for key in keys]
    # Scrap key delimiter escapes
    keys = ['<' if key == r'\<' else key for key in keys]
    for key in keys:
        assert key, 'Empty key detected. This is a bug.'

    # Reconstruct inputstring to detect parse errors
    verificationstring = keys_to_bytestring(keys)
    for i in range(len(inputstring)):
        if len(verificationstring) <= i or verificationstring[i] != inputstring[i]:
            raise ParseError(inputstring, verificationstring, i)

    for filename in filenames:
        doc = Document(filename)
        doc.activate()
        for key in keys:
            doc.ui.feedinput(key)

        doc.ui.feedinput(save)
        doc.ui.feedinput(force_quit)

        # The main loop of fate itself
        run()
