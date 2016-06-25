import re

re_number = re.compile(r'\d')
#re_string = re.compile(r'["\'][^"\']*["\']')
#"[^"]*"|'[^']*'
re_string = re.compile(r'"[^"]*"|\'[^\']*\'')

def regex_labels(highlighting, text, beg, end, l):
    """ Add a list l of (regex, label) to the labeling of doc """
    for regex, label in l:
        for match in text.finditer(regex):
            highlighting.highlight(match, label)
