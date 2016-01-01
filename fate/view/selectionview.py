from ..selection import Interval, Selection
from ..contract import post
from ..navigation import is_position_visible
from ..document import Document
from logging import debug


def refresh_selectionview_post(r, doc, old=None, new=None):
    assert r is None

    viewport_beg, viewport_end = doc.view.visible_interval
    opos_to_vpos = doc.view.opos_to_vpos

    viewport_vbeg = opos_to_vpos[viewport_beg]
    viewport_vend = opos_to_vpos[viewport_end]

    for vbeg, vend in doc.view.selection:
        assert viewport_vbeg <= vbeg <= vend <= viewport_vend


@post(refresh_selectionview_post)
def refresh_selectionview(doc, old=None, new=None):
    """
    Construct selection view.
    Use the opos_to_vpos mapping to derive the selection intervals in the viewport.
    Return nothing.
    Side effect: doc.view.selection is set.
    """
    viewport_beg, viewport_end = doc.view.visible_interval
    opos_to_vpos = doc.view.opos_to_vpos

    selectionview = Selection()
    for beg, end in doc.selection:
        # Only add selections when they should be visible
        if (viewport_beg < end and beg < viewport_end
                # Make sure empty intervals are taken into account, if they are visible
                # The visibility of an empty interval equals the visibility of the
                # position it prepends
                or beg == end and is_position_visible(doc, beg)):
            beg = max(beg, viewport_beg)
            end = min(viewport_end, end)
            vbeg = opos_to_vpos[beg]
            # Even though end is exclusive, and may be outside the text, it is being
            # mapped
            vend = opos_to_vpos[end]
            selectionview.add(Interval(vbeg, vend))
    debug('Viewport: {}'.format(Interval(viewport_beg, viewport_end)))
    debug('Selecion view: {}'.format(selectionview))
    doc.view.selection = selectionview


def init_refresh_selectionview(doc):
    doc.OnSelectionChange.add(refresh_selectionview)
Document.OnDocumentInit.add(init_refresh_selectionview)
