"""A selector takes a selection and returns another derived selection"""
from selection import Selection

# Maybe the fundamental selections from the doc should be here

def move_to_next_line(t, selection):
    """Move all intervals one line forwards"""
    result = Selection()
    for (beg, end) in selection:
        eol = t.find(t.eol_char, beg)
        if eol == -1:
            result.add((beg, end))
        else:
            bol = t.rfind(t.eol_char, 0, beg)
            result.add((eol + beg - bol, eol + end - bol))
    return result


def move_to_previous_line(t, selection):
    """Move all intervals one line backwards"""
    result = Selection()
    for (beg, end) in selection:
        bol = t.rfind(t.eol_char, 0, beg)
        if bol == -1:
            result.add((beg, end))
        else:
            bol2 = t.rfind(t.eol_char, 0, bol)
            result.add((bol2 + beg - bol, bol2 + end - bol))
    return result


def move_to_previous_char(t, selection):
    """Move all intervals one char backwards"""
    result = Selection()
    for (beg, end) in selection:
        # If further movement is impossible, do nothing
        if beg <= 0:
            return selection
        result.add((beg - 1, end - 1))
    return result


def move_to_next_char(t, selection):
    """Move all intervals one char forwards"""
    result = Selection()
    for (beg, end) in selection:
        # If further movement is impossible, do nothing
        if end >= len(t):
            return selection
        result.add((beg + 1, end + 1))
    return result
