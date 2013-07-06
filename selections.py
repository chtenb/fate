import text


def next_line(t, beg):
    """Get index for moving one line forwards"""
    eol = t.find(t.eol_char, beg)
    if eol == -1:
        return beg
    else:
        bol = t.rfind(t.eol_char, 0, beg)
        return eol + beg - bol


def previous_line(t, beg):
    """Get index for moving one line backwards"""
    bol = t.rfind(t.eol_char, 0, beg)
    if bol == -1:
        return beg
    else:
        bol2 = t.rfind(t.eol_char, 0, bol)
        return bol2 + beg - bol
