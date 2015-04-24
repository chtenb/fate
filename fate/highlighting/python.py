import re
from .common import regex_labels, re_number, re_string

import keyword
re_keyword = re.compile(r'\b({})\b'.format('|'.join(keyword.kwlist)))
re_comment = re.compile('#.*\n')

def init(doc):
    doc.OnGenerateGlobalHighlighting.add(main)

def main(doc):
    regex_list = [(re_keyword, 'keyword'), (re_number, 'number'), (re_string, 'string'),
                  (re_comment, 'comment')]
    regex_labels(doc, regex_list)
