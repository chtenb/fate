import re
from . import commands
from .selectors import SelectPattern, SelectLocalPattern


def local_find(document):
    key = document.ui.getkey()
    SelectLocalPattern(re.escape(key), document)(document)
commands.local_find = local_find


def local_find_backwards(document):
    key = document.ui.getkey()
    SelectLocalPattern(re.escape(key), document, reverse=True)(document)
commands.local_find_backwards = local_find_backwards


def search(document):
    document.search_pattern = document.ui.prompt('/')
    if document.search_pattern:
        try:
            SelectPattern(document.search_pattern, document)(document)
        except re.error as e:
            document.ui.notify(str(e))
commands.search = search


def search_current_content(document):
    document.search_pattern = re.escape(document.selection.content(document)[-1])
    SelectPattern(document.search_pattern, document)(document)
commands.search_current_content = search_current_content


def search_next(document):
    if document.search_pattern:
        SelectPattern(document.search_pattern, document)(document)
commands.search_next = search_next


def search_previous(document):
    if document.search_pattern:
        SelectPattern(document.search_pattern, document, reverse=True)(document)
commands.search_previous = search_previous
