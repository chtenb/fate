from math import ceil
from bisect import bisect_left
from logging import debug

from .selection import Interval, Selection
from .contract import post
from .navigation import (is_position_visible, move_n_wrapped_lines_down, count_wrapped_lines,
end_of_wrapped_line)


def _compute_selectionview_post(result, self, old=None, new=None):
    assert result is None

    viewport_beg, viewport_end = self.visible_interval
    opos_to_vpos = self.opos_to_vpos

    viewport_vbeg = opos_to_vpos[viewport_beg]
    viewport_vend = opos_to_vpos[viewport_end]

    for vbeg, vend in self.selection:
        assert viewport_vbeg <= vbeg <= vend <= viewport_vend


class TextView:

    """
    Comprise the text features that are shown in the userinterface for a given text interval.
    All the positions in the resulting text are adjusted w.r.t. the text concealments that may
    have been done.

    How does a UI known when a new TextView should be created?
    A TextView object consists of 3 parts w.r.t. to a text interval:
    - the text (including concealments)
    - selection
    - highlighting

    So if either the, start, length, text, selection, highlighting or concealment changes,
    the userinterface should create a new TextView object.
    However, if jus the selection of highlighting changes, one only should have to update
    those. This is currently possible by calling compute_highlighting or compute_highlighting.

    Positional computations often have to deal with two kinds of positions:
    position in the original text and in the resulting view text.
    For clarity we prepend every variable containing information relative to the original text
    with `o` and relative to the view text with `v`.
    """

    def __init__(self, doc, width: int, height: int):
        """
        Construct a textview for the given doc starting with (and relative to) position start
        with size of the given length.
        """
        self.doc = doc
        self.width = width
        self.height = height

        self.text = None
        self.selection = None
        self.highlighting = None

        self.viewpos_to_origpos = []
        self.origpos_to_viewpos = []

        self.compute_text()
        # FIXME
        # self.compute_selection()
        # self.compute_highlighting()

    def text_as_lines(self):
        """
        Return the text in the textview as a list of lines, where the lines are wrapped with
        self.width.
        """
        result = [line[self.width * i:self.width * (i + 1)]
                  for line in self.text.splitlines()
                  for i in range(ceil(len(line) / self.width))]
        print(len(result))
        print(count_wrapped_lines(self.text, self.width))
        assert len(result) == count_wrapped_lines(self.text, self.width)
        return result

    def compute_text(self):
        """
        Compute the concealed text and the corresponding position mapping.
        We don't have any guarantees to the length of the viewtext in terms of the length of the
        original text whatsoever.
        So we can only incrementally try to increase the length of th original text, until the
        viewtext covers the required length.
        Since normally the concealed text is not much (if any) larger, this should not lead
        to accidentally computing a way too large textview.
        """
        width, height = self.doc.ui.viewport_size

        otext = self.doc.text
        obeg = self.doc.ui.viewport_offset
        # Length of the sample of the original text that is used to compute the view text
        olength = 1

        vtext, opos_to_vpos, vpos_to_opos = self.compute_text_from_orig_interval(obeg, olength)
        assert opos_to_vpos[obeg] == 0
        while count_wrapped_lines(vtext, width) < height and obeg + olength < len(otext):
            olength *= 2
            vtext, opos_to_vpos, vpos_to_opos = self.compute_text_from_orig_interval(obeg, olength)

        # Everything should be snapped to exactly fit the required length.
        # This is to make textview behave as determenistic as possible, such that potential
        # indexing errors are identified soon.
        last_line = move_n_wrapped_lines_down(vtext, width, 0, height - 1)
        length = end_of_wrapped_line(vtext, width, last_line)

        # Extend mappings to allow (exclusive) interval ends to be mapped
        vpos_to_opos.append(olength + 1)
        opos_to_vpos.append(len(vtext) + 1)

        self.text = vtext[:length]
        self.viewpos_to_origpos = vpos_to_opos[:length + 1]
        self.origpos_to_viewpos = opos_to_vpos[:length + 1]

        assert len(self.text) == length
        assert len(self.viewpos_to_origpos) == length + 1
        assert len(self.origpos_to_viewpos) == length + 1

        # visible_text_length = move_n_wrapped_lines_down(textview, width, 0, height)
        # visible_interval = Interval(obeg, obeg + visible_text_length)
        # assert len(vpos_to_opos) >= visible_text_length
        # assert len(opos_to_vpos) >= obeg - opos


    def compute_text_from_orig_interval(self, obeg, olength):
        """
        Compute the concealed text and the corresponding position mapping from an interval in
        terms of the original text.
        """
        conceal = self.doc.conceal
        conceal.generate_local_substitutions(obeg, olength)

        # Construct a sorted list of relevant substitutions
        first_global_subst = bisect_left(conceal.global_substitutions, (Interval(obeg, obeg), ''))
        last_global_subst = bisect_left(conceal.global_substitutions,
                                        (Interval(obeg + olength, obeg + olength), ''))
        substitutions = (conceal.local_substitutions
                         + conceal.global_substitutions[first_global_subst:last_global_subst])
        substitutions.sort()

        vtext_builder = []  # Stringbuilder for text to be displayed
        vpos = 0  # Current position in view text, i.e. olength of text builded so far
        opos = obeg  # Current position in original text
        vpos_to_opos = []  # Mapping from view positions to original positions
        # Mapping from original positions (minus offset) to view positions
        opos_to_vpos = []
        otext = self.doc.text

        subst_index = 0
        while opos < olength:
            # Add remaining non-concealed text
            if subst_index >= len(substitutions):
                olength = min(olength - vpos, len(otext) - opos)
                vpos_to_opos.extend(range(opos, opos + olength))
                opos_to_vpos.extend(range(vpos, vpos + olength))
                vtext_builder.append(otext[opos:opos + olength])
                opos += olength
                vpos += olength
                break

            # sbeg and send are in terms of original positions
            (sbeg, send), replacement = substitutions[subst_index]

            # Add non-concealed text
            if sbeg > opos:
                # Bound viewtext by self.olength
                olength = min(sbeg - opos, olength - vpos)
                vpos_to_opos.extend(range(opos, opos + olength))
                opos_to_vpos.extend(range(vpos, vpos + olength))
                vtext_builder.append(otext[opos:opos + olength])
                vpos += olength
                opos += olength
            # Add concealed text
            else:
                vlength = len(replacement)
                olength = send - sbeg
                vpos_to_opos.extend(vlength * [opos])
                opos_to_vpos.extend(olength * [vpos])
                vtext_builder.append(replacement)
                vpos += vlength
                opos += olength
                subst_index += 1

        vtext = ''.join(vtext_builder)

        return vtext, opos_to_vpos, vpos_to_opos

    def compute_highlighting(self):
        # Construct highlighting view
        highlightingview = []
        for i in range(len(self.text)):
            opos = self.vpos_to_opos[i]
            if opos in self.doc.highlighting:
                highlightingview.append(self.doc.highlighting[opos])
            else:
                highlightingview.append('')
        self.highlighting = highlightingview

    @post(_compute_selectionview_post)
    def compute_selection(self, old=None, new=None):
        """
        Construct selection view.
        Use the opos_to_vpos mapping to derive the selection intervals in the viewport.
        Return nothing.
        Side effect: selection is set.
        """
        viewport_beg, viewport_end = self.visible_interval
        opos_to_vpos = self.opos_to_vpos

        selectionview = Selection()
        for obeg, end in self.doc.selection:
            # Only add selections when they should be visible
            if (viewport_beg < end and obeg < viewport_end
                    # Make sure empty intervals are taken into account, if they are visible
                    # The visibility of an empty interval equals the visibility of the
                    # position it prepends
                    or obeg == end and is_position_visible(self.doc, obeg)):
                obeg = max(obeg, viewport_beg)
                end = min(viewport_end, end)
                vbeg = opos_to_vpos[obeg]
                # Even though end is exclusive, and may be outside the text, it is being
                # mapped
                vend = opos_to_vpos[end]
                selectionview.add(Interval(vbeg, vend))
        debug('Viewport: {}'.format(Interval(viewport_beg, viewport_end)))
        debug('Selecion view: {}'.format(selectionview))
        self.selection = selectionview

