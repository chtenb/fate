import re
import keyword
from .common import regex_labels, re_number, re_string

re_keyword = re.compile(r'\b({})\b'.format('|'.join(keyword.kwlist)))
re_comment = re.compile('#.*\n')


def init(doc):
    doc.OnGenerateGlobalHighlighting.add(main)

def main(highlighting, text, beg, end):
    regex_list = [(re_keyword, 'keyword'), (re_number, 'number'), (re_string, 'string'),
                  (re_comment, 'comment')]
    regex_labels(highlighting, text, beg, end, regex_list)
