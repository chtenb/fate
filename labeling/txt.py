import re
from .common import regex_labels, re_number, re_string

keywords = ['TODO']

re_keyword = re.compile(r'\b({})\b'.format('|'.join(keywords)))


def init(document):
    document.OnGenerateLabeling.add(main)


def main(document):
    regex_list = [(re_keyword, 'keyword'), (re_number, 'number'), (re_string, 'string')]
    regex_labels(document, regex_list)
