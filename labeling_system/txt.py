from ..session import Session
import re

keywords = ['TODO']

re_keyword = re.compile(r'\b({})\b'.format('|'.join(keywords)))
re_number = re.compile('\d')

def main(session):
    for regex, label in [(re_keyword, 'keyword'), (re_number, 'number')]:
        matches = regex.finditer(session.text)
        for match in matches:
            session.labeling.add((match.start(), match.end()), label)

Session.OnGenerateLabeling.add(main)
