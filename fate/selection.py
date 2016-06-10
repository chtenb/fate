"""This module contains the Interval and the Selection class."""
from logging import debug

class Interval:

    def __init__(self, beg, end):
        if not 0 <= beg <= end:
            raise ValueError('({}, {}) is not a valid interval'.format(beg, end))
        self.beg = beg
        self.end = end

    def __getitem__(self, index):
        return (self.beg, self.end)[index]

    def __contains__(self, pos):
        return self.beg <= pos < self.end

    def __str__(self):
        return '({},{})'.format(self.beg, self.end)

    def __repr__(self):
        return 'Interval' + str(self)

    def __eq__(self, other):
        return (isinstance(other, Interval)
                and (self.beg, self.end) == (other.beg, other.end))

    def __lt__(self, other):
        if not isinstance(other, Interval):
            raise ValueError
        return (self.beg, self.end) < (other.beg, other.end)

    def __add__(self, other):
        """Add second interval to first interval."""
        if isinstance(other, Interval):
            return Interval(min(self.beg, other.beg), max(self.end, other.end))
        else:
            return NotImplemented

    def __sub__(self, other):
        """Substract second interval from first interval."""
        if isinstance(other, Interval):
            beg, end = self
            nbeg, nend = self
            mbeg, mend = other
            if mbeg <= beg:
                nbeg = max(beg, mend)
            if mend >= end:
                nend = min(end, mbeg)

            if nbeg <= nend:
                return Interval(nbeg, nend)
        else:
            return NotImplemented

    @property
    def isempty(self):
        return self.beg == self.end

    def content(self, doc):
        return doc.text[max(0, self.beg):min(len(doc.text), self.end)]

    def __hash__(self):
        return hash((self.beg, self.end))


class Selection:

    """
    Sorted list of disjoint non-adjacent intervals.

    TODO: allow adjacentness in selections?
    What about empty intervals?
    For users this stuff doesn't make sense, but for arbitrary substitutions used by
    e.g. plugins this may make sense.
    Proposal: allow it, but after each change in the user selection, call a function that
    merges adjacent things.
    """

    def __init__(self, intervals=None):
        self._intervals = []
        if intervals:
            self.add(intervals)

    def __getitem__(self, index):
        return self._intervals[index]

    def __setitem__(self, index, item):
        if not isinstance(item, Interval):
            raise ValueError('Selections can only contain intervals')
        self._intervals[index] = item

    def __len__(self):
        return len(self._intervals)

    def __repr__(self):
        return 'Selection: {}'.format(self)

    def __str__(self):
        return ', '.join(str(i) for i in self._intervals)

    def __eq__(self, obj):
        return (isinstance(obj, Selection)
                and self._intervals == obj._intervals)

    def __call__(self, doc):
        """Set self to be the current selection of the doc."""
        if not self.isempty:
            doc.selection = self

    @property
    def isempty(self):
        """Check if we have intervals."""
        return not bool(self._intervals)

    def validate(self, doc_or_text):
        """Raise exception if selection is not valid."""
        if isinstance(doc_or_text, str):
            text = doc_or_text
        else:
            text = doc_or_text.text

        if self.isempty:
            raise Exception('Selection is empty.')
        if not self._intervals[-1][1] <= len(text):
            raise Exception(
                'Selection {} is not valid for a text with length {}.'
                .format(self, len(text))
            )

    def content(self, doc_or_text):
        """Return the content of self."""
        if isinstance(doc_or_text, str):
            text = doc_or_text
        else:
            text = doc_or_text.text

        return [text[max(0, beg):min(len(text), end)]
                for beg, end in self]

    def index(self, interval):
        """Return the index of given interval."""
        return self._intervals.index(interval)

    def contains(self, pos):
        """Check if given position is contained in self."""
        for interval in self:
            beg, end = interval
            if beg <= pos < end:
                return interval

    def add(self, obj):
        """
        Add one or more intervals to the selection. If interval is overlapping
        with or adjacent to some existing interval, they are merged.
        obj must be an interval or a sequence of intervals.
        """
        if not isinstance(obj, Interval):
            for interval in obj:
                self.add(interval)
            return

        nbeg, nend = obj
        assert nbeg <= nend

        # First merge overlapping or adjacent existing intervals into the new interval
        for beg, end in self._intervals:
            # [  ]  existing interval
            #  (    new interval
            if beg < nbeg <= end:
                nbeg = beg
            # [  ]
            #   )
            if beg <= nend < end:
                nend = end

        # Then insert the new interval at the right index
        result = []
        added = False
        for beg, end in self._intervals:
            #  []    existing interval
            # (  )   new interval
            if not (nbeg <= beg and end <= nend):
                # [ ]
                #     ( )
                if end <= nbeg:
                    result.append(Interval(beg, end))
                #     [ ]
                # ( )
                elif nend <= beg:
                    if not added:
                        result.append(Interval(nbeg, nend))
                        added = True
                    result.append(Interval(beg, end))
        if not added:
            result.append(Interval(nbeg, nend))

        self._intervals = result
    def complement(self, doc_or_text):
        """Return the complementary selection of self."""
        intervals = [interval for in_selection, interval in self.partition(doc_or_text)
                     if not in_selection]
        return Selection(intervals)

    def bound(self, lower_bound, upper_bound):
        """Return the selection obtained by bounding self."""
        result = Selection()
        for beg, end in self:
            beg = max(beg, lower_bound)
            end = min(end, upper_bound)
            if not beg > end:
                result.add(Interval(beg, end))
        return result

    def partition(self, doc_or_text):
        """
        Return a sorted list containing all intervals in self
        together with all complementary intervals.
        """
        if isinstance(doc_or_text, str):
            text = doc_or_text
        else:
            text = doc_or_text.text

        positions = [pos for interval in self for pos in interval]
        positions.insert(0, 0)
        positions.append(len(text))
        in_selection = False

        result = []
        for i in range(1, len(positions)):
            interval = Interval(positions[i - 1], positions[i])
            result.append((in_selection, interval))
            in_selection = not in_selection

        return result

    def intersects(self, interval):
        """Check if interval intersects with self."""
        beg, end = interval
        for i in self:
            if beg <= i[0] < end or beg < i[1] <= end or i[0] < beg and end < i[1]:
                return True
        return False

    def __add__(self, obj):
        """
        Return the selection obtained by adding obj to self.
        obj can be an interval or a sequence of intervals.
        """
        result = Selection()
        result.add(self)
        result.add(obj)
        return result

    def __radd__(self, obj):
        return self + obj

    def substract(self, obj):
        """Remove one or more intervals from the selection."""
        if not isinstance(obj, Interval):
            for interval in obj:
                self.substract(interval)
            return

        nbeg, nend = obj
        assert nbeg <= nend

        result = []
        # Iterate through existing intervals and cut them
        for beg, end in self._intervals:
            #   [  ]   existing interval
            # )      ( given interval
            if nend <= beg or end <= nbeg:
                result.append(Interval(beg, end))
            else:
                # [  ]
                #  (
                if beg < nbeg < end:
                    result.append(Interval(beg, nbeg))
                # [  ]
                #   )
                if beg < nend < end:
                    result.append(Interval(nend, end))

        if result:
            self._intervals = result

    def __sub__(self, obj):
        """
        Return the selection obtained by substracting obj to self.
        obj can be an interval or a sequence of intervals.
        """
        result = Selection()
        result.add(self)
        result.substract(obj)
        return result

    def __rsub__(self, obj):
        return self - obj

