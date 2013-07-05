import text

def next_line(t, start):
    """@todo: Docstring for next_line

    :t: text
    :start: index
    :returns: index

    """
    next_line = t.find_char(start, '\n')
    return next_line + start
