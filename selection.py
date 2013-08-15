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

    def add(self, interval):
        """Add interval to the selection. If interval is overlapping
        with some existing interval, they are merged."""
        (nbeg, nend) = interval
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
                    result.append(interval)
                    added = True
                result.append((beg, end))
            else:
                # [  ]
                #  (
                if beg < nbeg < end - 1:
                    interval = (beg, nend)
                # [  ]
                #   )
                if beg < nend - 1 < end:
                    interval = (nbeg, end)

        if not added:
            result.append(interval)

        self._intervals = result

    def remove(self, interval):
        """Remove interval from selection"""
        self._intervals.remove(interval)
