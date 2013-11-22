from ..session import Session
import re
from .common import regex_labels, re_number

import keyword
re_keyword = re.compile(r'\b({})\b'.format('|'.join(keyword.kwlist)))
re_comment = re.compile('#.*\n')
# TODO: prevent counting quotes in comments
re_string = re.compile('["\'][^"\']*["\']')


def main(session):
    regex_list = [(re_keyword, 'keyword'), (re_number, 'number'), (re_string, 'string'), (re_comment, 'comment')]
    regex_labels(session, regex_list)

Session.OnGenerateLabeling.add(main)
