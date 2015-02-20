import re
from . import commands
from .selectors import selectpattern, select_local_pattern, intervalselector
from .document import Document
from .prompt import prompt
from .commandtools import Compose
from functools import partial

Document.search_pattern = ''


def local_find(document):
    key = document.ui.getkey()
    selector = intervalselector(partial(select_local_pattern, re.escape(key)))
    selector(document)
commands.local_find = local_find


def local_find_backward(document):
    key = document.ui.getkey()
    selector = intervalselector(partial(select_local_pattern, re.escape(key), reverse=True))
    selector(document)
commands.local_find_backward = local_find_backward


def _search(document):
    document.search_pattern = document.promptinput
    if document.search_pattern:
        try:
            selectpattern(document.search_pattern, document, document.selection,
                          document.selectmode)(document)
        except re.error as e:
            document.ui.notify(str(e))
commands.search = Compose(prompt('/'), _search)


def search_current_content(document):
    document.search_pattern = re.escape(document.selection.content(document)[-1])
    selectpattern(document.search_pattern, document, document.selection,
                  document.selectmode)(document)
commands.search_current_content = search_current_content


def search_next(document):
    if document.search_pattern:
        selectpattern(document.search_pattern, document, document.selection,
                      document.selectmode)(document)
commands.search_next = search_next


def search_previous(document):
    if document.search_pattern:
        selectpattern(document.search_pattern, document, document.selection,
                      document.selectmode, reverse=True)(document)
commands.search_previous = search_previous
