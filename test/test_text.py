from itertools import chain, combinations, combinations_with_replacement
from .basetestcase import BaseTestCase
from ..operation import Operation
from ..selection import Selection, Interval

def non_empty_powerset(iterable):
    "powerset([1,2,3]) --> (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r + 1) for r in range(len(s)))

class TextTest(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)
        l = len(self.sampletext)
        intervalspace = [Interval(0, 0), Interval(0, 3), Interval(7, 10),
                         Interval(15, l), Interval(l, l)]
        contentspace = ['', 'a', 'abcdefghijklmnopqrstuvwxyz']
        selectionlist = [Selection(intervals) for intervals in non_empty_powerset(intervalspace)]

        # Compute all possible selection/operation combinations
        self.selection_operation_list = []
        for selection in selectionlist:
            # Compute appropriate content
            newcontentlist = combinations_with_replacement(contentspace, len(selection))
            for newcontent in newcontentlist:
                selection_operation = (selection, Operation(self.document, newcontent))
                self.selection_operation_list.append(selection_operation)

        #print('Number of cases: ' + str(len(self.selection_operation_list)))

    def test_str(self):
        self.assertEqual(self.sampletext, str(self.document.text))

        for selection, operation in self.selection_operation_list:
            self.document.selection = selection
            self.document.text.preview(operation)
            previewtext = str(self.document.text)
            self.document.text.apply(operation)
            finaltext = str(self.document.text)

            #print(previewtext)
            #print('----------------------------------------------')
            #print(finaltext)
            self.assertEqual(previewtext, finaltext)
            self.document.undotree.undo()

