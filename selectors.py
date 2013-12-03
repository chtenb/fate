"""A selector takes a selection and returns a second, derived selection. We distinguish between functions that work selection-wise
(selectors) and function that work interval-wise (interval selectors)."""
from .selection import Selection
from .operation import Operation
from .session import select_mode, extend_mode, reduce_mode
import re
import logging

# NOTE: to implement selectors generically, we probably need them to be generators, just like patterns
# In case of next_char, this would mean that it starts yielding beg until len(text)
# This way we can iterate until we have a changed selection/interval (just like we already do for patterns
# An alternative to this is moving the mode stuff to pattern_selector, and decorate pattern directly with @selector

def to_selection(obj):
    if obj.__class__ == Operation:
        obj.session.apply(obj)
        return obj.new_selection
    elif obj.__class__ == Selection:
        return obj
    else:
        raise Exception('Only Selections and Operations can be applied')


def selector(function):
    def wrapper(obj):
        selection = to_selection(obj)
        session = selection.session
        text = session.text

        result = function(selection, text, session.selection_mode)

        # If the result is empty, we return the old selection
        if not result:
            return selection

        # If the result is invalid, we return the original selection
        for beg, end in result:
            if not (0 <= beg < len(text) and 0 <= end <= len(text)):
                return selection

        return result
    return wrapper


@selector
def single_interval(selection, text, mode):
    return Selection(selection.session, intervals=selection[0])


@selector
def empty(selection, text, mode):
    x = selection[0][0]
    return Selection(selection.session, intervals=[(x, x)])


@selector
def everything(selection, text, mode):
    return Selection(selection.session, intervals=[(0, len(text))])


@selector
def join(selection, text, mode):
    return Selection(selection.session, intervals=[(selection[0][0], selection[-1][1])])


@selector
def complement(selection, text, mode):
    return selection.complement()


def global_selector(function):
    @selector
    def wrapper(selection, text, mode):
        if mode == reduce_mode:
            result = function(selection.complement(), text)
            if result:  # result can be None
                result = selection.reduce(result)
        elif mode == extend_mode:
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
    """An interval selector takes an interval to another interval.
    This induces a selector, by applying the interval
    selector to all intervals contained in a selection.
    Keeps original interval when resulting interval is invalid."""
    @selector
    def wrapper(selection, text, mode):
        if mode == reduce_mode:
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

            if mode == reduce_mode or mode == extend_mode:
                interval_result = min(interval[0], interval_result[0]), max(interval[1], interval_result[1])
            result.append(interval_result)

        result = Selection(selection.session, result)
        if mode == reduce_mode:
            result = selection.reduce(result)
            if result:
                return result
            return selection
        return result
    return wrapper


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
            if mode == extend_mode:
                new_selection = selection.extend(new_selection)
            elif mode == reduce_mode:
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
                if mode == extend_mode:
                    new_selection = selection.extend(new_selection)
                elif mode == reduce_mode:
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
                # If match is in the right direction
                if not reverse and mend > beg or reverse and mbeg < end:
                    if mode == extend_mode:
                        new_interval = min(beg, mbeg), max(end, mend)
                    elif mode == reduce_mode:
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
    return (local_pattern_selector(pattern, **kwargs),
            local_pattern_selector(pattern, reverse=True, **kwargs))


next_char, previous_char = pattern_pair(r'(?s).')
next_word, previous_word = pattern_pair(r'\b\w+\b')
next_line, previous_line = pattern_pair(r'\s*([^\n]*)', group=1)
next_full_line, previous_full_line = pattern_pair(r'[^\n]*\n?')
next_paragraph, previous_paragraph = pattern_pair(r'(?s)((?:[^\n][\n]?)+)')
