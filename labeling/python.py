import re
from .common import regex_labels, re_number

import keyword
re_keyword = re.compile(r'\b({})\b'.format('|'.join(keyword.kwlist)))
re_comment = re.compile('#.*\n')
# TODO: prevent counting quotes in comments
re_string = re.compile('["\'][^"\']*["\']')

def init(document):
    document.OnGenerateLabeling.add(main)

def main(document):
    regex_list = [(re_keyword, 'keyword'), (re_number, 'number'), (re_string, 'string'),
                  (re_comment, 'comment')]
    regex_labels(document, regex_list)
