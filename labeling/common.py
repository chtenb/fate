import re

re_number = re.compile(r'\d')
re_string = re.compile(r'["\'][^"\']*["\']')

def regex_labels(document, l):
    """ Add a list of (regex, label) to the labeling of document """
    for regex, label in l:
        matches = regex.finditer(document.text)
        for match in matches:
            document.labeling.add((match.start(), match.end()), label)
