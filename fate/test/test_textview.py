from logging import debug
from .basetestcase import BaseTestCase
from ..selection import Selection, Interval

from ..textview import TextView, IntervalMapping


class TestTextView(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)

    def test_interval_mapping(self):
        mapping = IntervalMapping(5)
        interval = Interval(2,3)
        image = Interval(2, 10)
        mapping.append(interval, image)
        self.assertEqual(mapping[interval], mapping[image])

    def test_creation_without_conceal(self):
        for text in ['', '123456789', '\n\n\n\n\n']:
            self.doc.text = text
            for selection in [Selection([Interval(0, 0)]),
                              Selection([Interval(0, len(text))])]:
                self.doc.selection = selection
                for width in range(1, 6):
                    TextView.for_entire_text(self.doc, width)
                    for offset in range(max(1, len(text))):
                        for height in range(1, 6):
                            TextView.for_screen(self.doc, width, height, offset)
