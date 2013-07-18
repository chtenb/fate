class Selection:
    """Sorted list of disjoint intervals"""

    def __init__(self, intervals=None):
        if intervals != None:
            self._intervals = intervals
        else:
            self._intervals = []

    def __getitem__(self, index):
        return self._intervals[index]

    def __len__(self):
        return len(self._intervals)

    def __str__(self):
        return str(self._intervals)

    def add(self, new):
        """Add interval to the selection. If interval is overlapping
        with some existing interval, they are merged."""
        (nbeg, nend) = new
        if nbeg > nend:
            raise Exception(
                "Invalid interval: end cannot be smaller than begin")

        result = []
        added = False
        for (beg, end) in self._intervals:
            # [ ]       existing interval
            #     ( )   new interval
            if end <= nbeg:
                result.append((beg, end))
            #     [ ]
            # ( )
            elif end <= nbeg:
                if not added:
                    result.append(new)
                    added = True
                result.append((beg, end))
            else:
                # [  ]
                #  (
                if beg < nbeg < end - 1:
                    new = (beg, nend)
                # [  ]
                #   )
                if beg < nend - 1 < end:
                    new = (nbeg, end)

        if not added:
            result.append(new)

        self._intervals = result

    def remove(self, interval):
        """Remove interval from selection"""
        self._intervals.remove(interval)

    # Maybe should be in operators
    def partition(self, text):
        """Return a selection containing all intervals in the selection
        together with all complementary intervals"""
        selection_len = len(self)
        text_len = len(text)
        result = Selection()

        if not self or self[0][0] > 0:
            if not self:
                complement_end = text_len
            else:
                complement_end = self[0][0]
            result.add((0, complement_end))

        for i, (beg, end) in enumerate(self):
            if i + 1 == selection_len:
                complement_end = text_len
            else:
                complement_end = self[i + 1][0]
            result.add((beg, end))
            result.add((end, complement_end))
        return result

    # Maybe should be in operators
    def bound(self, lower_bound, upper_bound):
        return Selection([(max(beg, lower_bound), min(end, upper_bound))
                          for beg, end in self
                          if beg < upper_bound or end > lower_bound])
