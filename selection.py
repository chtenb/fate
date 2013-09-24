class Selection:
    """Sorted list of disjoint non-adjacent intervals"""
    def __init__(self, session, intervals=None):
        self.session = session

        self._intervals = []
        if intervals:
            for interval in intervals:
                self.add(interval)

    def __getitem__(self, index):
        return self._intervals[index]

    def __len__(self):
        return len(self._intervals)

    def __str__(self):
        return str(self._intervals)

    def index(self, interval):
        return self._intervals.index(interval)

    def contains(self, position):
        for beg, end in self:
            if beg <= position < end:
                return (beg, end)

    def add(self, interval):
        """Add interval to the selection. If interval is overlapping
        with or adjacent to some existing interval, they are merged."""
        nbeg, nend = interval
        if nbeg > nend:
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

    def extend(self, selection):
        """Return the selection obtained by extending self with the selector's return"""
        result = Selection(self.session, intervals=self._intervals)
        for interval in selection:
            result.add(interval)
        return result

    def reduce(self, selection):
        """Return the selection obtained by reducing self with the selector's return.
        Reducing is defined by extending the complement of self"""
        return self.complement().extend(selection).complement()

    def complement(self):
        """Return the complementary selection of self"""
        return Selection(self.session, intervals=[interval for in_selection, interval in self.partition()
                                                  if not in_selection])

    def partition(self, lower_bound=0, upper_bound=float('infinity')):
        """Return a sorted list containing all intervals in self
        together with all complementary intervals"""
        text = self.session.text
        points = [point for interval in self for point in interval]
        in_selection = True
        if not points or points[0] > 0:
            points.insert(0, 0)
            in_selection = False
        if not points or points[-1] < len(text):
            points.append(len(text))

        result = []
        for i in range(1, len(points)):
            beg, end = points[i - 1], points[i]
            if beg < upper_bound or end > lower_bound:
                result.append((in_selection, (max(beg, lower_bound), min(end, upper_bound))))
            in_selection = not in_selection
        return result
