"""This module contains the Selection class."""
from .action import Action


class Selection(Action):
    """Sorted list of disjoint non-adjacent intervals"""
    def __init__(self, session, intervals=None):
        Action.__init__(self, session)
        self.previous_selection = session.selection

        self._intervals = []
        if intervals:
            for interval in intervals:
                self.add(interval)
        else:
            self.add((0, 0))

    def __getitem__(self, index):
        return self._intervals[index]

    def __len__(self):
        return len(self._intervals)

    def __str__(self):
        return str(self._intervals)

    def __eq__(self, selection):
        return selection.__class__ == Selection and self._intervals == selection._intervals

    def _do(self):
        """Set selection to be the current selection of the session."""
        self.session.selection = self

    def _undo(self):
        """Set current selection to previous selection."""
        self.session.selection = self.previous_selection

    def index(self, interval):
        """Return the index of `interval`."""
        return self._intervals.index(interval)

    def contains(self, position):
        """Check if position is contained in self"""
        for beg, end in self:
            if beg <= position < end:
                return (beg, end)

    def add(self, interval):
        """Add interval to the selection. If interval is overlapping
        with or adjacent to some existing interval, they are merged."""
        nbeg, nend = interval
        if nbeg != None and nend != None and nbeg > nend:
            raise Exception("Invalid interval " + str(interval))

        # First merge overlapping or adjacent existing intervals into the new interval
        for (beg, end) in self._intervals:
            # [  ]
            #  (
            if beg < nbeg <= end:
                nbeg = beg
            # [  ]
            #   )
            if beg <= nend < end:
                nend = end

        # Then insert the new interval at the right index
        result = []
        added = False
        for (beg, end) in self._intervals:
            #  []    existing interval
            # (  )   new interval
            if not (nbeg <= beg and end <= nend):
                # [ ]
                #     ( )
                if end <= nbeg:
                    result.append((beg, end))
                #     [ ]
                # ( )
                elif nend <= beg:
                    if not added:
                        result.append((nbeg, nend))
                        added = True
                    result.append((beg, end))

        if not added:
            result.append((nbeg, nend))

        self._intervals = result

    def remove(self, interval):
        """Remove interval from the selection."""
        nbeg, nend = interval
        if nbeg > nend:
            raise Exception("Invalid interval " + str(interval))

        result = []
        for beg, end in self._intervals:
            #   [  ]   existing interval
            # )      ( new interval
            if nend <= beg or end <= nbeg:
                result.append((beg, end))
            else:
                # [  ]
                #  (
                if beg < nbeg < end:
                    result.append((beg, nbeg))
                # [  ]
                #   )
                if beg < nend < end:
                    result.append((nend, end))

        self._intervals = result

    def extend(self, selection):
        """Return the selection obtained by extending self with the selector's return"""
        result = Selection(self.session, self._intervals)
        for interval in selection:
            result.add(interval)
        return result

    def reduce(self, selection):
        """Return the selection obtained by reducing self with the selector's return."""
        result = Selection(self.session, self._intervals)
        for interval in selection:
            result.remove(interval)
        return result

    def complement(self):
        """Return the complementary selection of self"""
        intervals = [interval for in_selection, interval in self.partition()
                     if not in_selection]
        return Selection(self.session, intervals)

    def bound(self, lower_bound=None, upper_bound=None):
        """Return the selection obtained by bounding self"""
        if not lower_bound:
            lower_bound = 0
        if not upper_bound:
            upper_bound = len(self.session.text)

        result = Selection(self.session)
        for beg, end in self:
            beg = max(beg, lower_bound)
            end = min(end, upper_bound)
            if not beg > end:
                result.add((beg, end))
        return result

    def partition(self):
        """Return a sorted list containing all intervals in self
        together with all complementary intervals"""
        text = self.session.text
        points = [point for interval in self for point in interval]
        points.insert(0, 0)
        points.append(len(text))
        in_selection = False

        result = []
        for i in range(1, len(points)):
            interval = points[i - 1], points[i]
            result.append((in_selection, interval))
            in_selection = not in_selection
        return result

    def intersects(self, interval):
        """Check if interval intersects with self"""
        beg, end = interval
        for i in self:
            if beg <= i[0] < end or beg < i[1] <= end or i[0] < beg and end < i[1]:
                return True
        return False

