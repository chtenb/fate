import re
from . import commands
from .selecting.selectpattern import selectpattern, select_local_pattern
from .selecting.decorators import intervalselector_withmode
from .document import Document
from .prompt import prompt
from .commandtools import Compose
from functools import partial

Document.search_pattern = ''


def local_find(document):
    key = document.ui.getkey()
    command = intervalselector_withmode(partial(select_local_pattern, re.escape(key)))
    command(document)
commands.local_find = local_find


def local_find_backward(document):
    key = document.ui.getkey()
    command = intervalselector_withmode(partial(select_local_pattern, re.escape(key),
                                                reverse=True))
    command(document)
commands.local_find_backward = local_find_backward


def _search(document):
    document.search_pattern = document.promptinput
    if document.search_pattern:
        try:
            command = selectpattern(document.search_pattern, document, document.selection)
            command(document)
        except re.error as e:
            document.ui.notify(str(e))
commands.search = Compose(prompt('/'), _search)


def search_current_content(document):
    document.search_pattern = re.escape(document.selection.content(document)[-1])
    command = selectpattern(document.search_pattern, document, document.selection)
    command(document)
commands.search_current_content = search_current_content


def search_next(document):
    if document.search_pattern:
        try:
            command = selectpattern(document.search_pattern, document, document.selection)
            command(document)
        except re.error as e:
            document.ui.notify(str(e))
commands.search_next = search_next


def search_previous(document):
    if document.search_pattern:
        try:
            command = selectpattern(document.search_pattern,
                                    document, document.selection, reverse=True)
            command(document)
        except re.error as e:
            document.ui.notify(str(e))
commands.search_previous = search_previous
