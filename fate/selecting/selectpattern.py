import re
from logging import debug
from ..selection import Selection, Interval
from .decorators import intervalselector_withmode, partial
from .. import commands


def findpattern(text, pattern, reverse=False, group=0):
    """Find intervals that match given pattern."""
    matches = re.finditer(pattern, text)
    if reverse:
        matches = reversed(list(matches))
    return [Interval(match.start(group), match.end(group))
            for match in matches]


def selectpattern(pattern, doc, selection, reverse=False, group=0):
    newselection = Selection()
    selection = selection or doc.selection

    match_intervals = findpattern(doc.text, pattern, reverse, group)

    # First select all occurences intersecting with selection,
    # and process according to mode
    new_intervals = [interval for interval in match_intervals
                     if selection.intersects(interval)]
    if new_intervals:
        new_selection = Selection(new_intervals)
        if new_selection and selection != new_selection:
            newselection.add(new_selection)
            return newselection

    # If that doesnt change the selection,
    # start selecting one by one, and process according to mode
    new_intervals = []
    if reverse:
        beg, end = selection[-1]
    else:
        beg, end = selection[0]

    for mbeg, mend in match_intervals:
        new_selection = Selection(Interval(mbeg, mend))
        # If match is in the right direction
        if not reverse and mend > beg or reverse and mbeg < end:
            if new_selection and selection != new_selection:
                newselection.add(new_selection)
                return newselection

    return newselection


def select_local_pattern(pattern, text, interval, reverse=False,
                         group=0, only_within=False, allow_same_interval=False):

    match_intervals = findpattern(text, pattern, reverse, group)

    beg, end = interval
    new_interval = None

    for mbeg, mend in match_intervals:
        # If only_within is True, match must be within current interval
        if only_within and not (beg <= mbeg and mend <= end):
            continue

        # If allow_same_interval is True, allow same interval as original
        if allow_same_interval and (beg, end) == (mbeg, mend):
            return Interval(mbeg, mend)

        if not reverse and beg < mend:
            new_interval = Interval(mbeg, mend)
        elif reverse and mbeg < end:
            new_interval = Interval(mbeg, mend)

        # If suitable interval found, return it
        if new_interval and new_interval != interval:
            return new_interval


def selectindent(text, interval):
    pattern = r'(?m)^([ \t]*)'
    # To avoid edge cases, we first select the entire line
    fullline = selectfullline(text, interval)
    return select_local_pattern(pattern, text, fullline, allow_same_interval=True,
                                reverse=True, only_within=True, group=1)
commands.selectindent = intervalselector_withmode(selectindent)


selectline = partial(select_local_pattern, r'(?m)^[ \t]*([^\n]*)', group=1,
                     allow_same_interval=True)
commands.selectline = intervalselector_withmode(selectline)


def selectfullline(text, interval):
    pattern = r'(?m)^[^\n]*\n?'
    result1 = select_local_pattern(pattern, text, interval, allow_same_interval=True)
    # If we have an empty interval at the end of the text, result1 will we none;
    # we have to match backward.
    result2 = select_local_pattern(pattern, text, interval, allow_same_interval=True,
                                   reverse=True)
    return result1 or result2
commands.selectfullline = intervalselector_withmode(selectfullline)


def patternpair(pattern, **kwargs):
    """
    Return two local pattern selectors for given pattern,
    one matching forward and one matching backward.
    """
    return (partial(select_local_pattern, pattern, **kwargs),
            partial(select_local_pattern, pattern, reverse=True, **kwargs))

selectnextchar, selectpreviouschar = patternpair(r'(?s).')
commands.selectnextchar = intervalselector_withmode(selectnextchar)
commands.selectpreviouschar = intervalselector_withmode(selectpreviouschar)
selectnextword, selectpreviousword = patternpair(r'\b\w+\b')
commands.selectnextword = intervalselector_withmode(selectnextword)
commands.selectpreviousword = intervalselector_withmode(selectpreviousword)
selectnextclass, selectpreviousclass = patternpair(r'\w+|[ \t]+|[^\w \t\n]+')
commands.selectnextclass = intervalselector_withmode(selectnextclass)
commands.selectpreviousclass = intervalselector_withmode(selectpreviousclass)
selectnextline, selectpreviousline = patternpair(r'(?m)^[ \t]*([^\n]*)', group=1)
commands.selectnextline = intervalselector_withmode(selectnextline)
commands.selectpreviousline = intervalselector_withmode(selectpreviousline)
selectnextfullline, selectpreviousfullline = patternpair(r'[^\n]*\n?')
commands.selectnextfullline = intervalselector_withmode(selectnextfullline)
commands.selectpreviousfullline = intervalselector_withmode(selectpreviousfullline)
selectnextparagraph, selectpreviousparagraph = patternpair(r'(?s)((?:[^\n][\n]?)+)')
commands.selectnextparagraph = intervalselector_withmode(selectnextparagraph)
commands.selectpreviousparagraph = intervalselector_withmode(selectpreviousparagraph)
selectnextwhitespace, selectpreviouswhitespace = patternpair(r'\s')
commands.selectnextwhitespace = intervalselector_withmode(selectnextwhitespace)
commands.selectpreviouswhitespace = intervalselector_withmode(selectpreviouswhitespace)
