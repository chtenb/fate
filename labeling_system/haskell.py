from ..document import Document
import re
from .common import regex_labels, re_number


keywords = ['module', 'let', 'in', 'where', 'import', 'hiding', 'type', 'data', 'newtype', 'case', 'of', 'do', 'if', 'then', 'else',
            'instance', 'class', 'return', 'as']

re_keyword = re.compile(r'\b({})\b'.format('|'.join(keywords)))
re_comment = re.compile('--.*\n')
re_string = re.compile('["][^"]*["]')


def main(document):
    regex_list = [(re_keyword, 'keyword'), (re_number, 'number'), (re_string, 'string'), (re_comment, 'comment')]
    regex_labels(document, regex_list)

Document.OnGenerateLabeling.add(main)
