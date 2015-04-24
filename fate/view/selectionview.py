from bisect import bisect_left
from logging import debug
from ..selection import Interval, Selection


def refresh_selectionview(doc):
    # Construct selection view
    # Find starting interval in selection
    # debug(self.substitutions)
    viewport_offset = doc.ui.viewport_offset
    textview_length = doc.view.text_length
    opos_to_vpos = doc.view.opos_to_vpos

    selection_start = bisect_left(doc.selection, Interval(viewport_offset,
                                                          viewport_offset))
    selection_end = bisect_left(doc.selection, Interval(textview_length,
                                                        textview_length))

    selectionview = Selection()
    #debug(doc.selection[selection_start:selection_end])
    for beg, end in doc.selection[selection_start:selection_end]:
        beg = max(0, beg - viewport_offset)
        end = min(textview_length, end - viewport_offset)
        vbeg = opos_to_vpos[beg]
        vend = opos_to_vpos[end]
        # vend = opos_to_vpos[end - 1] + 1 # End is after last position in interval
        selectionview.add(Interval(vbeg, vend))
    doc.view.selection = selectionview
