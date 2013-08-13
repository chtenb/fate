from .selection import Selection


class Operation:
    """Container of modified content of a selection"""
    def __init__(self, session, selection, new_content):
        self.session = session

        self.old_selection = selection
        self.old_content = session.selection.content()
        self.new_content = new_content

        self.new_selection = Selection(session)
        beg = selection[0][0]
        end = beg + len(self.new_content[0])
        self.new_selection.add((beg, end))
        for i in range(1, len(selection)):
            beg = end + selection[i][0] - selection[i - 1][1]
            end = beg + len(self.new_content[i])
            self.new_selection.add((beg, end))

    def apply(self):
        """Apply the operation to the text"""
        for i, interval in enumerate(self.old_selection):
            self.session.text.set(interval, self.new_content[i])
