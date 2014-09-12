from itertools import chain, combinations, combinations_with_replacement
from .basetestcase import BaseTestCase
from ..operation import Operation
from ..selection import Selection, Interval
from ..text import Text
import re


class TextTest(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)

    def test_default(self):
        self.assertEqual(self.sampletext, str(self.document.text))

        text = Text('asdf')
        print(re.findall('a', text))
        print(text.find('f'))

    def test_apply(self):
        self.document.selection = Selection((Interval(7, 10), Interval(18, 20)))
        operation = Operation(self.document, ['abc', 'Abc'])
        self.document.text.apply(self.document, operation)
        expected = (self.sampletext[:7] + 'abc' + self.sampletext[10:18]
                    + 'Abc' + self.sampletext[20:])
        self.assertEqual(expected, str(self.document.text))

    def test_preview(self):
        """Relies on apply to be correct."""
        l = len(self.sampletext)
        intervalspace = [Interval(0, 0), Interval(0, 3), Interval(7, 10),
                         Interval(15, l), Interval(l, l)]
        contentspace = ['', 'a', 'abcdefghijklmnopqrstuvwxyz']
        selectionlist = [Selection(intervals) for intervals in non_empty_powerset(intervalspace)]

        # Compute all possible selection/operation combinations
        selection_operation_list = []
        for selection in selectionlist:
            # Compute appropriate content
            newcontentlist = combinations_with_replacement(contentspace, len(selection))
            for newcontent in newcontentlist:
                selection_operation = (selection, Operation(self.document, newcontent))
                selection_operation_list.append(selection_operation)

        #print('Number of cases: ' + str(len(self.selection_operation_list)))

        for selection, operation in selection_operation_list:
            self.document.selection = selection
            self.document.text.preview(operation)
            previewtext = str(self.document.text)
            self.document.text.apply(self.document, operation)
            finaltext = str(self.document.text)

            # print(previewtext)
            # print('----------------------------------------------')
            # print(finaltext)
            self.assertEqual(previewtext, finaltext)
            self.document.undotree.undo()


def non_empty_powerset(iterable):
    "powerset([1,2,3]) --> (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r + 1) for r in range(len(s)))
