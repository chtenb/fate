from ..session import Session
import re

todo = re.compile(r'TODO')
def main(session):
    matches = todo.finditer(session.text)
    for match in matches:
        session.labeling.add((match.start(), match.end()), 'keyword')

Session.OnGenerateLabeling.add(main)
