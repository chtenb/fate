from ..session import Session
import re
from .common import regex_labels, re_number, re_string

keywords = ['TODO']

re_keyword = re.compile(r'\b({})\b'.format('|'.join(keywords)))

def main(session):
    regex_list = [(re_keyword, 'keyword'), (re_number, 'number'), (re_string, 'string')]
    regex_labels(session, regex_list)

Session.OnGenerateLabeling.add(main)
