from functools import wraps
from ..selection import Selection, Interval
from . import SelectModes

def partial(func, *args, name='', docs='', **keywords):
    """Pragmatic solution for being able to set a name for a partial function"""
    @wraps(func)
    def wrapper(*fargs, **fkeywords):
        newkeywords = keywords.copy()
        newkeywords.update(fkeywords)
        return func(*(args + fargs), **newkeywords)
    wrapper.func = func
    wrapper.args = args
    wrapper.keywords = keywords
    wrapper.name = name
    wrapper.docs = docs
    return wrapper


def selector(function):
    """Turn given selector in a command that takes a document."""
    @wraps(function)
    def wrapper(doc, *args, selection=None, selectmode=None, preview=False, **kwargs):
        selection = selection or doc.selection
        selectmode = selectmode or doc.selectmode

        result = function(
            doc, *args, selection=selection, selectmode=selectmode, **kwargs)

        if preview:
            return result
        if result != None:
            result(doc)
    return wrapper


def intervalselector(function):
    """Turn given intervalselector in a command that takes a document."""
    @wraps(function)
    @selector
    def wrapper(doc, selection, *args, selectmode=None, **kwargs):
        new_intervals = []
        for interval in selection:
            new_interval = function(doc, interval, *args, selectmode=selectmode, **kwargs)
            if new_interval == None:
                return
            new_intervals.append(new_interval)
        return Selection(new_intervals)
    return wrapper


def intervalselector_withmode(function):
    """
    Turn given intervalselector in a command that takes a document and process
    according to selectmode.
    """
    @wraps(function)
    @intervalselector
    def wrapper(doc, interval, *args, selectmode=None, **kwargs):
        # Give different interval based on selectmode
        beg, end = interval
        if selectmode == SelectModes.head:
            proxy_interval = Interval(end, end)
        elif selectmode == SelectModes.tail:
            proxy_interval = Interval(beg, beg)
        else:
            proxy_interval = interval

        new_interval = function(doc, proxy_interval, *args, **kwargs)
        if new_interval == None:
            return

        # Process interval differently based on selectmode
        nbeg, nend = new_interval
        if selectmode == SelectModes.head:
            # beg is fixed, but end is determined by new interval
            if nend <= end:
                return Interval(beg, max(beg, nbeg))
            else:
                return Interval(beg, max(beg, nend))
        elif selectmode == SelectModes.tail:
            # end is fixed, but beg is determined by new interval
            if nbeg >= beg:
                return Interval(min(end, nend), end)
            else:
                return Interval(min(end, nbeg), end)
        else:
            return new_interval
    return wrapper


