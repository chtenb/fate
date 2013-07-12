import text


class Selection:
    """Sorted list of disjoint intervals"""
    _intervals = []

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
            raise Exception("Invalid interval: end cannot be smaller than begin")

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
        self._intervals.remove(interval)
