"""A selector takes a selection and returns another derived selection"""
from selection import Selection


def partition(selection, text):
    """Return a selection containing all intervals in the selection
    together with all complementary intervals"""
    points = [point for interval in selection for point in interval]
    if not points or points[0] > 0:
        points.insert(0, 0)
    if not points or points[-1] < len(text):
        points.append(len(text))

    result = Selection()
    for i in range(1, len(points)):
        result.add((points[i - 1], points[i]))
    return result


def bound(selection, lower_bound, upper_bound):
    return Selection([(max(beg, lower_bound), min(end, upper_bound))
                      for beg, end in selection
                      if beg < upper_bound or end > lower_bound])


def move_to_next_line(selection, text):
    """Move all intervals one line forwards"""
    result = Selection()
    for (beg, end) in selection:
        eol = text.find(text.eol_char, beg)
        if eol == -1:
            result.add((beg, end))
        else:
            bol = text.rfind(text.eol_char, 0, beg)
            result.add((eol + beg - bol, eol + end - bol))
    return result


def move_to_previous_line(selection, text):
    """Move all intervals one line backwards"""
    result = Selection()
    for (beg, end) in selection:
        bol = text.rfind(text.eol_char, 0, beg)
        if bol == -1:
            result.add((beg, end))
        else:
            bol2 = text.rfind(text.eol_char, 0, bol)
            result.add((bol2 + beg - bol, bol2 + end - bol))
    return result


def move_to_previous_char(selection, text):
    """Move all intervals one char backwards"""
    result = Selection()
    for (beg, end) in selection:
        # If further movement is impossible, do nothing
        if beg <= 0:
            return selection
        result.add((beg - 1, end - 1))
    return result


def move_to_next_char(selection, text):
    """Move all intervals one char forwards"""
    result = Selection()
    for (beg, end) in selection:
        # If further movement is impossible, do nothing
        if end >= len(text):
            return selection
        result.add((beg + 1, end + 1))
    return result
