from bisect import bisect_left
from logging import debug

from .selection import Interval, Selection
from .contract import post
from .navigation import is_position_visible
from .document import Document
from .navigation import move_n_wrapped_lines_down


def _compute_selectionview_post(r, self, old=None, new=None):
    assert r is None

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

    So if either the text, selection, highlighting or concealment changes, the userinterface
    should create a new TextView object.
    However, if jus the selection of highlighting changes, one only should have to update
    those. This is currently possible by calling compute_highlighting or compute_highlighting.
    """

    # TODO: be able to define number of lines with max width in terms of the concealed text
    def __init__(self, doc, start: int, length: int):
        """
        Construct a textview for the given doc starting with (and relative to) position start
        with size of the given length.
        """
        self.doc = doc
        self.start = start
        self.length = length

        self.text = None
        self.selection = None
        self.highlighting = None

        self.viewpos_to_origpos = []
        self.origpos_to_viewpos = []

        self.compute_text()
        self.compute_selection()
        self.compute_highlighting()

    def compute_text(self):
        """
        Compute the concealed text and the corresponding position mapping.
        """
        conceal = self.doc.conceal
        conceal.generate_local_substitutions(self.start, self.length)

        # Construct a sorted list of relevant substitutions
        first_global_subst = bisect_left(
            conceal.global_substitutions, (Interval(self.start, self.start), ''))
        last_global_subst = bisect_left(conceal.global_substitutions, (Interval(self.start + self.length,
                                                                             self.start + self.length), ''))
        substitutions = (conceal.local_substitutions +
                         conceal.global_substitutions[first_global_subst:last_global_subst])
        substitutions.sort()

        textview_builder = []  # Stringbuilder for text to be displayed
        vpos = 0  # Current position in view text, i.e. length of text builded so far
        opos = self.start  # Current position in original text
        vpos_to_opos = []  # Mapping from view positions to original positions
        # Mapping from original positions (minus offset) to view positions
        opos_to_vpos = []
        text = self.doc.text

        subst_index = 0
        while vpos < self.length and opos < len(text):
            # Add remaining non-concealed text
            if subst_index >= len(substitutions):
                length = min(self.length - vpos, len(text) - opos)
                vpos_to_opos.extend(range(opos, opos + length))
                opos_to_vpos.extend(range(vpos, vpos + length))
                textview_builder.append(text[opos:opos + length])
                opos += length
                vpos += length
                break

            # sbeg and send are in terms of original positions
            (sbeg, send), replacement = substitutions[subst_index]

            # Add non-concealed text
            if sbeg > opos:
                # Bound viewtext by self.length
                length = min(sbeg - opos, self.length - vpos)
                vpos_to_opos.extend(range(opos, opos + length))
                opos_to_vpos.extend(range(vpos, vpos + length))
                textview_builder.append(text[opos:opos + length])
                vpos += length
                opos += length
            # Add concealed text
            else:
                vlength = len(replacement)
                olength = send - sbeg
                vpos_to_opos.extend(vlength * [opos])
                opos_to_vpos.extend(olength * [vpos])
                textview_builder.append(replacement)
                vpos += vlength
                opos += olength
                subst_index += 1

        # Extend mappings to allow (exclusive) interval ends to be mapped
        vpos_to_opos.append(opos + 1)
        opos_to_vpos.append(vpos + 1)

        textview = ''.join(textview_builder)

        self.text = textview
        width, height = self.doc.ui.viewport_size
        self.visible_text_length = move_n_wrapped_lines_down(textview, width, 0, height)
        self.vpos_to_opos = vpos_to_opos
        self.opos_to_vpos = opos_to_vpos
        self.visible_interval = Interval(self.start, self.start + self.visible_text_length)

        # debug(vpos_to_opos)
        # debug(opos_to_vpos)
        assert len(vpos_to_opos) >= self.visible_text_length
        assert len(opos_to_vpos) >= self.start - opos

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
        for beg, end in self.doc.selection:
            # Only add selections when they should be visible
            if (viewport_beg < end and beg < viewport_end
                    # Make sure empty intervals are taken into account, if they are visible
                    # The visibility of an empty interval equals the visibility of the
                    # position it prepends
                    or beg == end and is_position_visible(self.doc, beg)):
                beg = max(beg, viewport_beg)
                end = min(viewport_end, end)
                vbeg = opos_to_vpos[beg]
                # Even though end is exclusive, and may be outside the text, it is being
                # mapped
                vend = opos_to_vpos[end]
                selectionview.add(Interval(vbeg, vend))
        debug('Viewport: {}'.format(Interval(viewport_beg, viewport_end)))
        debug('Selecion view: {}'.format(selectionview))
        self.selection = selectionview

