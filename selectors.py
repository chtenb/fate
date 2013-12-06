"""A selector is a function that is decorated by `selector`, either directly or indirectly. It is an action that is used to modify that
selection of the session. We distinguish between functions that work selection-wise (global selectors) and function that work interval-wise
(local selectors). Furthermore we have selectors that are based on regular expressions."""
from .selection import Selection
from .modes import SELECT_MODE, EXTEND_MODE, REDUCE_MODE
import re


def selector(function):
    """This is a decorator. The passed function will be turned into a selector and will be given a selection, text and selection mode."""
    def wrapper(session):
        selection = session.selection
        text = session.text

        result = function(selection, text, session.selection_mode)

        # If the result is empty or invalid, we keep the original
        if not result:
            return
        for beg, end in result:
            if not (0 <= beg < len(text) and 0 <= end <= len(text)):
                return

        session.selection = result
    return wrapper


@selector
def single_interval(selection, text, mode):
    """Reduce the selection to a single interval."""
    return Selection(selection.session, intervals=selection[0])


@selector
def empty(selection, text, mode):
    """Reduce the selection to a single empty interval."""
    beg = selection[0][0]
    return Selection(selection.session, intervals=[(beg, beg)])


@selector
def everything(selection, text, mode):
    """Select the entire text."""
    return Selection(selection.session, intervals=[(0, len(text))])


@selector
def join(selection, text, mode):
    """Join all intervals together."""
    return Selection(selection.session, intervals=[(selection[0][0], selection[-1][1])])


@selector
def complement(selection, text, mode):
    """Return the complement."""
    return selection.complement()


def global_selector(function):
    """This is a decorator. The passed function will be turned into a global selector and will be given a selection, text and selection mode."""
    @selector
    def wrapper(selection, text, mode):
        if mode == REDUCE_MODE:
            result = function(selection.complement(), text)
            if result:  # result can be None
                result = selection.reduce(result)
        elif mode == EXTEND_MODE:
            result = function(selection, text)
            if result:  # result can be None
                result = selection.extend(result)
        else:
            result = function(selection, text)

        return result
    return wrapper


@global_selector
def move_to_previous_line(selection, text):
    """Move all intervals one line backwards"""
    interval = selection[0]
    beg, end = interval
    bol = text.rfind('\n', 0, beg)
    if bol == -1:
        return interval
    bol2 = text.rfind('\n', 0, bol)
    return Selection(selection.session, intervals=[(min(bol, bol2 + beg - bol), min(bol, bol2 + end - bol))])


@global_selector
def move_to_next_line(selection, text):
    """Move all intervals one line forwards"""
    interval = selection[-1]
    beg, end = interval
    eol = text.find('\n', beg)
    if eol == -1:
        return interval
    bol = text.rfind('\n', 0, beg)
    return Selection(selection.session, intervals=[(max(eol, eol + beg - bol), max(eol, eol + end - bol))])


def local_selector(function):
    """A local selector takes an interval to another interval. This induces a selector, by applying the interval selector to all intervals contained in a selection. Keeps original interval when resulting interval is invalid."""
    @selector
    def wrapper(selection, text, mode):
        if mode == REDUCE_MODE:
            iterselection = selection.complement()
        else:
            iterselection = selection

        result = []
        for interval in iterselection:
            interval_result = function(interval, text)

            # If the result invalid, we take the original interval
            if not interval_result:
                interval_result = interval
            else:
                beg, end = interval_result
                if not (0 <= beg < len(text) and 0 <= end <= len(text)):
                    interval_result = interval

            if mode == REDUCE_MODE or mode == EXTEND_MODE:
                interval_result = min(interval[0], interval_result[0]), max(interval[1], interval_result[1])
            result.append(interval_result)

        result = Selection(selection.session, result)
        if mode == REDUCE_MODE:
            result = selection.reduce(result)
            if result:
                return result
            return selection
        return result
    return wrapper


@local_selector
def empty_before(interval, text):
    """Return the empty interval before each interval."""
    beg, end = interval
    return (beg, beg)


@local_selector
def empty_after(interval, text):
    """Return the empty interval after each interval."""
    beg, end = interval
    return (end, end)

# TODO: select inside brackets (or maybe even more general: select between two separators)


def global_pattern_selector(pattern, reverse=False, group=0):
    """Factory method for creating global selectors based on a regular expression"""
    @selector
    def wrapper(selection, text, mode):
        matches = re.finditer(pattern, text)
        if reverse:
            matches = reversed(list(matches))

        match_intervals = []
        for match in matches:
            match_intervals.append((match.start(group), match.end(group)))

        # First select all occurences intersecting with selection, and process according to mode
        new_intervals = []
        for interval in match_intervals:
            if selection.intersects(interval):
                new_intervals.append(interval)

        if new_intervals:
            new_selection = Selection(selection.session, intervals=new_intervals)
            if mode == EXTEND_MODE:
                new_selection = selection.extend(new_selection)
            elif mode == REDUCE_MODE:
                new_selection = selection.reduce(new_selection)

            if new_selection and selection != new_selection:
                return new_selection

        # If that doesn't change the selection, start selecting one by one, and process according to mode
        new_intervals = []
        if reverse:
            beg, end = selection[-1]
        else:
            beg, end = selection[0]

        for mbeg, mend in match_intervals:
            new_selection = Selection(selection.session, intervals=[(mbeg, mend)])
            # If match is in the right direction
            if not reverse and mend > beg or reverse and mbeg < end:
                if mode == EXTEND_MODE:
                    new_selection = selection.extend(new_selection)
                elif mode == REDUCE_MODE:
                    new_selection = selection.reduce(new_selection)

                if new_selection and selection != new_selection:
                    return new_selection

    return wrapper


def local_pattern_selector(pattern, reverse=False, group=0):
    """Factory method for creating local selectors based on a regular expression"""
    @selector
    def wrapper(selection, text, mode):

        def reduce_interval(self, interval):
            beg, end = self
            nbeg, nend = self
            mbeg, mend = interval
            if mbeg <= beg:
                nbeg = max(beg, mend)
            if mend >= end:
                nend = min(end, mbeg)

            if nbeg <= nend:
                return nbeg, nend

        matches = re.finditer(pattern, text)
        if reverse:
            matches = reversed(list(matches))

        match_intervals = []
        for match in matches:
            match_intervals.append((match.start(group), match.end(group)))

        new_intervals = []
        for interval in selection:
            beg, end = interval
            new_interval = None

            for mbeg, mend in match_intervals:
                # If match is valid
                # i.e. overlaps (or is empty and adjacent)
                # or is beyond current interval in right direction
                if not reverse and (mend > beg or mbeg == beg) or reverse and (mbeg < end or mend == end):
                    if mode == EXTEND_MODE:
                        new_interval = min(beg, mbeg), max(end, mend)
                    elif mode == REDUCE_MODE:
                        if reverse:
                            mend = max(end, mend)
                        else:
                            mbeg = min(beg, mbeg)
                        new_interval = reduce_interval(interval, (mbeg, mend))
                    else:
                        new_interval = mbeg, mend

                    if new_interval and new_interval != interval:
                        break

            # If the result invalid, we take the original interval
            if not new_interval:
                new_interval = interval

            new_intervals.append(new_interval)

        return Selection(selection.session, intervals=new_intervals)
    return wrapper


def pattern_pair(pattern, **kwargs):
    """Return two local pattern selectors for given pattern, one matching forward and one matching backward."""
    return (local_pattern_selector(pattern, **kwargs),
            local_pattern_selector(pattern, reverse=True, **kwargs))


next_char, previous_char = pattern_pair(r'(?s).')
next_word, previous_word = pattern_pair(r'\b\w+\b')
next_line, previous_line = pattern_pair(r'\s*([^\n]*)', group=1)
next_full_line, previous_full_line = pattern_pair(r'[^\n]*\n?')
next_paragraph, previous_paragraph = pattern_pair(r'(?s)((?:[^\n][\n]?)+)')
next_white_space, previous_white_space = pattern_pair(r'\s')
