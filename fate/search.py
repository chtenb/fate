import re
from . import commands
from .selecting.selectpattern import selectpattern, select_local_pattern
from .selecting.decorators import intervalselector_withmode
from .document import Document
from .commandtools import compose
from functools import partial
import logging

Document.search_pattern = ''


def local_find(doc):
    key = doc.ui.getkey()
    command = intervalselector_withmode(partial(select_local_pattern, re.escape(key)))
    command(doc)
commands.local_find = local_find


def local_find_backward(doc):
    key = doc.ui.getkey()
    command = intervalselector_withmode(partial(select_local_pattern, re.escape(key),
                                                reverse=True))
    command(doc)
commands.local_find_backward = local_find_backward


# TODO: fix search have correct promptstring
# TODO: make searching work again
def ask_search_string(doc):
    doc.modes.prompt.promptstring = '/'
    return doc.modes.prompt
def execute_search(doc):
    doc.search_pattern = doc.modes.prompt.inputstring
    logging.debug('Pattern: ' + doc.search_pattern)
    if doc.search_pattern:
        try:
            command = selectpattern(doc.search_pattern, doc, doc.selection)
            command(doc)
        except re.error as e:
            doc.ui.notify(str(e))
commands.search = compose(ask_search_string, execute_search, name='search')


def search_current_content(doc):
    doc.search_pattern = re.escape(doc.selection.content(doc)[-1])
    command = selectpattern(doc.search_pattern, doc, doc.selection)
    command(doc)
commands.search_current_content = search_current_content


def search_next(doc):
    if doc.search_pattern:
        try:
            command = selectpattern(doc.search_pattern, doc, doc.selection)
            command(doc)
        except re.error as e:
            doc.ui.notify(str(e))
commands.search_next = search_next


def search_previous(doc):
    if doc.search_pattern:
        try:
            command = selectpattern(doc.search_pattern,
                                    doc, doc.selection, reverse=True)
            command(doc)
        except re.error as e:
            doc.ui.notify(str(e))
commands.search_previous = search_previous
