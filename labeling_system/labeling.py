class Labeling(dict):
    """A Labeling is a mapping from the text to string labels"""

    def add(self, interval, label):
        beg, end = interval
        for position in range(beg, end):
            self[position] = label
