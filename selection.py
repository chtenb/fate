#!/bin/env python3.0


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

    def partition(self, text):
        """Return a list containing all intervals in the selection 
        together with all complementary intervals tupled with a boolean 
        indicating wether the interval is in the selection"""
        selection_len = len(self)
        text_len = len(text)

        if not self or self[0][0] > 0:
            if not self:
                complement_end = text_len
            else:
                complement_end = self[0][0]
            yield (0, complement_end), False

        for i, (beg, end) in enumerate(self):
            if i + 1 == selection_len:
                complement_end = text_len
            else:
                complement_end = self[i + 1][0]
            yield (beg, end), True
            yield (end, complement_end), False
