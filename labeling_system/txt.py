from ..session import Session
import re

todo = re.compile(r'TODO')
def main(session):
    matches = todo.finditer(session.text)
    for match in matches:
        for position in range(match.start(), match.end()):
            session.labeling[position] = 'keyword'

Session.OnGenerateLabeling.add(main)
