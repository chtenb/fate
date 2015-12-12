from ..selection import Interval, Selection


def refresh_selectionview(doc):
    """Construct selection view"""
    viewport_offset = doc.ui.viewport_offset
    textview_length = doc.view.text_length
    opos_to_vpos = doc.view.opos_to_vpos

    selectionview = Selection()
    for beg, end in doc.selection:
        beg = max(0, beg - viewport_offset)
        end = min(textview_length, end - viewport_offset)
        vbeg = opos_to_vpos[beg]
        # Even though end is exclusive, and may be outside the text, it is being mapped
        vend = opos_to_vpos[end]
        selectionview.add(Interval(vbeg, vend))
    doc.view.selection = selectionview
