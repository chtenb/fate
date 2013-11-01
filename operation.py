# from .selection import Selection
import copy


class Operation:
    """Container of modified content of a selection"""
    def __init__(self, session, selection, new_content):
        self.old_selection = selection
        self.old_content = session.content(selection)
        self.new_content = new_content

        beg = selection[0][0]
        end = beg + len(self.new_content[0])
        self.new_selection = Selection(session, [(beg, end)])
        for i in range(1, len(selection)):
            beg = end + selection[i][0] - selection[i - 1][1]
            end = beg + len(self.new_content[i])
            self.new_selection.add((beg, end))

    def inverse(self):
        result = copy.copy(self)
        result.old_selection, result.new_selection = result.new_selection, result.old_selection
        result.old_content, result.new_content = result.new_content, result.old_content
        return result

# TODO
# Implement solve_delete_chars and solve_backspace_chars
# Implement reverse string (which changes backspaces to deletes and vice versa)


def reverse(string):
    """Reverse string, and change backspaces into deletes and vice versa"""
    result = []
    for c in reversed(string):
        if c == '\b':
            result.append('\x7f')
        elif c == '\x7f':
            result.append('\b')
        else:
            result.append(c)
    return ''.join(result)


def solve_backspace_chars(string):
    """Evaluate all backspace characters"""
    result = []
    count = 0
    for c in reversed(string):
        if c == '\b':
            count += 1
        elif count > 0:
            count -= 1
        else:
            result.append(c)
    return ''.join(reversed(result))


def solve_delete_chars(string):
    """Evaluate all delete characters"""
    result = []
    count = 0
    for c in string:
        if c == '\x7f':
            count += 1
        elif count > 0:
            count -= 1
        else:
            result.append(c)
    return ''.join(result)
