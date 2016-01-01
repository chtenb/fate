"""
A concealment allows to replace parts of the text for purposes of improving the view.
Global concealments are concealments that need context, e.g. strings.
Local conceal do not, like plain string replacements, or simple locally checkable
regular expressions.
"""
from bisect import bisect_left
from logging import debug

from ..document import Document
from ..event import Event
from ..selection import Interval
from ..navigation import move_n_wrapped_lines_down



def init_conceal(doc):
    doc.view.conceal = Conceal(doc)

    doc.OnGenerateGlobalConceal = Event('OnGenerateGlobalConceal')
    doc.OnGenerateLocalConceal = Event('OnGenerateLocalConceal')

    doc.OnTextChanged.add(doc.view.conceal.generate_global_substitutions)

    # Example concealment that does not need any context
    doc.OnGenerateLocalConceal.add(conceal_tabs)

    # Examples
    # doc.OnGenerateGlobalConceal.add(conceal_eol)

Document.OnDocumentInit.add(init_conceal)


class Conceal:

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

    def refresh(self, doc):
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

        textview_builder = []  # Stringbuilder for text to be displayed
        vpos = 0  # Current position in view text, i.e. length of text builded so far
        opos = viewport_offset  # Current position in original text
        vpos_to_opos = []  # Mapping from view positions to original positions
        # Mapping from original positions (minus offset) to view positions
        opos_to_vpos = []
        text = self.doc.text

        subst_index = 0
        while vpos < max_length and opos < len(text):
            # Add remaining non-concealed text
            if subst_index >= len(substitutions):
                length = min(max_length - vpos, len(text) - opos)
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
                # Bound viewtext by max_length
                length = min(sbeg - opos, max_length - vpos)
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

        self.doc.view.text = textview
        visible_text_length = move_n_wrapped_lines_down(textview, width, 0, height)
        self.doc.view.visible_text_length = visible_text_length
        self.doc.view.vpos_to_opos = vpos_to_opos
        self.doc.view.opos_to_vpos = opos_to_vpos
        self.doc.view.visible_interval = Interval(doc.ui.viewport_offset,
                                                  doc.ui.viewport_offset
                                                  + doc.view.visible_text_length)

        # debug(vpos_to_opos)
        # debug(opos_to_vpos)
        assert len(vpos_to_opos) >= visible_text_length
        assert len(opos_to_vpos) >= viewport_offset - opos


def conceal_tabs(doc, start_pos, max_length):
    for i in range(start_pos, start_pos + max_length):
        if i >= len(doc.text):
            break
        if doc.text[i] == '\t':
            # viewstring = ' ' * (doc.tabwidth - 1) + '\u21E5'
            viewstring = ' ' * doc.tabwidth
            doc.view.conceal.local_substitute(Interval(i, i + 1), viewstring)


def conceal_eol(doc):
    for i in range(len(doc.text)):
        if i >= len(doc.text):
            break
        if doc.text[i] == '\n':
            doc.view.conceal.global_substitute(Interval(i, i + 1), '$\n')
