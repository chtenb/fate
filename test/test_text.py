from .basetestcase import BaseTestCase
from ..operation import Operation
from ..selection import Selection, Interval


class TextTest(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)
        self.session.selection = Selection(Interval(7, 10))
        self.operation = Operation(self.session, [''])

    def test_str(self):
        self.assertEqual(self.sampletext, str(self.session.text))

    def test_len(self):
        self.assertEqual(142, len(self.session.text))

    def test_get_position(self):
        for i, c in enumerate(self.sampletext):
            self.assertEqual(self.session.text.get_position(i), c)

        self.session.text.preview(self.operation)

        print(self.session.text)

        for i, c in enumerate(self.sampletext[:7] + self.sampletext[10:]):
            self.assertEqual(self.session.text.get_position(i), c)
