from ..session import Session
import re

import keyword
re_keywords = re.compile(r'\b({})\b'.format('|'.join(keyword.kwlist)))
re_numbers = re.compile('\d')
re_strings = re.compile('".*"')


def main(session):
    for regex, label in [(re_keywords, 'keyword'), (re_numbers, 'number'), (re_strings, 'string')]:
        matches = regex.finditer(session.text)
        for match in matches:
            session.labeling.add((match.start(), match.end()), label)

Session.OnGenerateLabeling.add(main)
