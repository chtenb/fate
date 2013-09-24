import re

re_number = re.compile('\d')
re_string = re.compile('["\'][^"\']*["\']')

def regex_labels(session, l):
    """ Add a list of (regex, label) to the labeling of session """
    for regex, label in l:
        matches = regex.finditer(session.text)
        for match in matches:
            session.labeling.add((match.start(), match.end()), label)
