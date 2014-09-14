import re
from . import commands
from .selectors import selectpattern, select_local_pattern
from .document import Document
from .prompt import Prompt
from .commandtools import Compose

Document.search_pattern = ''


def local_find(document):
    key = document.ui.getkey()
    select_local_pattern(re.escape(key), document)(document)
commands.local_find = local_find


def local_find_backwards(document):
    key = document.ui.getkey()
    select_local_pattern(re.escape(key), document, reverse=True)(document)
commands.local_find_backwards = local_find_backwards


def _search(document):
    document.search_pattern = document.promptinput
    if document.search_pattern:
        try:
            selectpattern(document.search_pattern, document)(document)
        except re.error as e:
            document.ui.notify(str(e))
commands.search = Compose(Prompt, _search)


def search_current_content(document):
    document.search_pattern = re.escape(document.selection.content(document)[-1])
    selectpattern(document.search_pattern, document)(document)
commands.search_current_content = search_current_content


def search_next(document):
    if document.search_pattern:
        selectpattern(document.search_pattern, document)(document)
commands.search_next = search_next


def search_previous(document):
    if document.search_pattern:
        selectpattern(document.search_pattern, document, reverse=True)(document)
commands.search_previous = search_previous
