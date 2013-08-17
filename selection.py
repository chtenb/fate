class Selection:
    """Sorted list of disjoint intervals"""
    def __init__(self, intervals=None):
        self._intervals = []
        if intervals != None:
            for interval in intervals:
                self.add(interval)

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
            raise Exception("Invalid interval " + str(interval) + ": end cannot be smaller than begin")

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

    def partition(selection, text):
        """Return a selection containing all intervals in the selection
        together with all complementary intervals"""
        points = [point for interval in selection for point in interval]
        if not points or points[0] > 0:
            points.insert(0, 0)
        if not points or points[-1] < len(text):
            points.append(len(text))

        result = Selection()
        for i in range(1, len(points)):
            result.add((points[i - 1], points[i]))
        return result

    def bound(selection, lower_bound, upper_bound):
        return Selection([(max(beg, lower_bound), min(end, upper_bound))
                          for beg, end in selection
                          if beg < upper_bound or end > lower_bound])
