from ..document import Document
from ..event import Event
from ..selection import Interval, Selection

from bisect import bisect_left, bisect_right
from logging import debug


class Conceal():

    """Functionality for text concealment."""

    def __init__(self, doc):
        self.doc = doc

        # Lists of (interval, new_content) pairs
        self.global_substitutions = []
        self.local_substitutions = []

    def local_substitute(self, interval, newcontent):
        self.local_substitutions.append((interval, newcontent))

    def global_substitute(self, interval, newcontent):
        self.global_substitutions.append((interval, newcontent))

    def generate_local_substitutions(self, viewport_offset, max_length):
        """
        This method is executed on-the-fly when the textview is generated, so it should
        never have to be called from any other place.
        """
        self.local_substitutions = []
        self.doc.OnGenerateLocalConceal.fire(self.doc, viewport_offset, max_length)
        self.local_substitutions.sort()

    def generate_global_substitutions(self, doc):
        """
        This method is by default only executed OnTextChanged.
        """
        self.global_substitutions = []
        self.doc.OnGenerateGlobalConceal.fire(self.doc)
        self.global_substitutions.sort()

    def refresh_textview(self, doc):
        """
        Compute a piece of text for the UI to display.
        Updates textview and the corresponding positions mappings.
        """
        viewport_offset = self.doc.ui.viewport_offset
        width, height = self.doc.ui.viewport_size
        max_length = width * height + 1
        self.generate_local_substitutions(viewport_offset, max_length)

        # Construct a sorted list of relevant substitutions
        first_global_subst = bisect_left(self.global_substitutions,
                                         (Interval(viewport_offset, viewport_offset), ''))
        last_global_subst = bisect_left(self.global_substitutions,
                                        (Interval(viewport_offset + max_length,
                                                  viewport_offset + max_length), ''))
        substitutions = (self.local_substitutions +
                         self.global_substitutions[first_global_subst:last_global_subst])
        substitutions.sort()

        viewport_offset = self.doc.ui.viewport_offset
        textview_builder = []  # Stringbuilder for text to be displayed
        vpos = 0  # Current position in view text, i.e. length of text builded so far
        opos = viewport_offset  # Current position in original text
        vpos_to_opos = []  # Mapping from view positions to original positions
        opos_to_vpos = []  # Mapping from original positions (minus offset) to view positions
        text = self.doc.text

        subst_index = 0
        while vpos < max_length and opos < len(text):
            # Add remaining non-concealed text
            if subst_index >= len(substitutions):
                length = max_length - vpos
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
                length = min(sbeg - opos, max_length - vpos)  # Bound viewtext by max_length
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

        textview_length = vpos
        textview = ''.join(textview_builder)
        assert len(textview) == textview_length
        assert textview_length <= max_length

        self.doc.ui.textview = textview
        self.doc.ui.textview_length = textview_length
        self.doc.ui.vpos_to_opos = vpos_to_opos
        self.doc.ui.opos_to_vpos = opos_to_vpos

        debug(vpos_to_opos)
        debug(opos_to_vpos)
        assert len(vpos_to_opos) >= textview_length
        assert len(opos_to_vpos) >= viewport_offset - opos

        # TODO: move stuff below to different functions

        # Construct labeling view
        labelingview = []
        for i in range(len(textview)):
            opos = vpos_to_opos[i]
            if opos in self.doc.labeling:
                labelingview.append(self.doc.labeling[opos])
            else:
                labelingview.append('')
        self.doc.ui.labelingview = labelingview

        # Construct selection view
        # Find starting interval in selection
        # debug(self.substitutions)
        selection_start = bisect_left(self.doc.selection, Interval(viewport_offset,
                                                                   viewport_offset))
        selection_end = bisect_left(self.doc.selection, Interval(textview_length,
                                                                 textview_length))
        selectionview = Selection()
        debug(self.doc.selection[selection_start:selection_end])
        for beg, end in self.doc.selection[selection_start:selection_end]:
            beg = max(0, beg - viewport_offset)
            end = min(textview_length, end - viewport_offset)
            debug(len(opos_to_vpos))
            debug((beg, end))
            vbeg = opos_to_vpos[beg]
            vend = opos_to_vpos[end]
            # vend = opos_to_vpos[end - 1] + 1 # End is after last position in interval
            debug((vbeg, vend))
            selectionview.add(Interval(vbeg, vend))
        self.doc.ui.selectionview = selectionview

        debug(labelingview)
        debug(selectionview)


def init_events(doc):
    doc.OnGenerateGlobalConceal = Event()
    doc.OnGenerateLocalConceal = Event()
    doc.conceal = Conceal(doc)

    doc.OnTextChanged.add(doc.conceal.generate_global_substitutions)
    doc.OnSelectionChange.add(doc.conceal.refresh_textview)
    doc.OnGenerateLocalConceal.add(conceal_tabs)
    doc.OnGenerateGlobalConceal.add(conceal_eol)


def conceal_tabs(doc, start_pos, max_length):
    for i in range(start_pos, start_pos + max_length):
        if i >= len(doc.text):
            break
        if doc.text[i] == '\t':
            doc.conceal.local_substitute(Interval(i, i + 1), ' ' * doc.tabwidth)


def conceal_eol(doc):
    for i in range(len(doc.text)):
        if i >= len(doc.text):
            break
        if doc.text[i] == '\n':
            doc.conceal.global_substitute(Interval(i, i + 1), '$\n')

Document.OnDocumentInit.add(init_events)
