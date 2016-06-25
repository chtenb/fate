import re
from .common import regex_labels, re_number, re_string


keywords = ['break', 'case', 'catch', 'continue', 'debugger', 'default', 'delete', 'do',
            'else', 'finally', 'for', 'function', 'if', 'in', 'instanceof', 'new',
            'return', 'switch', 'this', 'throw', 'try', 'typeof', 'var', 'void', 'while',
            'with']

re_keyword = re.compile(r'\b({})\b'.format('|'.join(keywords)))
re_comment = re.compile('//.*\n')


def init(document):
    document.OnGenerateGlobalHighlighting.add(main)


def main(highlighting, text, beg, end):
    regex_list = [(re_keyword, 'keyword'), (re_number, 'number'), (re_string, 'string'),
                  (re_comment, 'comment')]
    regex_labels(highlighting, text, beg, end, regex_list)
