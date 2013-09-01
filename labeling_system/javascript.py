from ..session import Session
import re


keywords = ['break', 'case', 'catch', 'continue', 'debugger', 'default', 'delete', 'do', 'else', 'finally', 'for', 'function', 'if', 'in', 'instanceof', 'new', 'return', 'switch', 'this', 'throw', 'try', 'typeof', 'var', 'void', 'while', 'with']

re_keyword = re.compile(r'\b({})\b'.format('|'.join(keywords)))
re_number = re.compile('\d')
re_string = re.compile('["\'][^"\']*["\']')
re_comment = re.compile('//.*\n')


def main(session):
    for regex, label in [(re_keyword, 'keyword'), (re_number, 'number'), (re_string, 'string'), (re_comment, 'comment')]:
        matches = regex.finditer(session.text)
        for match in matches:
            session.labeling.add((match.start(), match.end()), label)

Session.OnGenerateLabeling.add(main)
