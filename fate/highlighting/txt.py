import re
from .common import regex_labels, re_number, re_string

keywords = ['TODO']

re_keyword = re.compile(r'\b({})\b'.format('|'.join(keywords)))


def init(doc):
    doc.OnGenerateGlobalHighlighting.add(main)


def main(highlighting, text, beg, end):
    regex_list = [(re_keyword, 'keyword'), (re_number, 'number'), (re_string, 'string')]
    regex_labels(highlighting, text, beg, end, regex_list)
