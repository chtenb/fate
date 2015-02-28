from .. import ErrorChecker
from tempfile import gettempdir
import subprocess
import re
from ...selection import Interval
from ...navigation import coord_to_position

from logging import debug

ERROR_REGEX = re.compile(r'(.+):(\d+):(\d+): (.+)\n')


class Pep8Checker(ErrorChecker):

    name = 'pep8'

    def __init__(self):
        pass

    def check(self, document):
        tempfile = gettempdir() + '/' + document.filename.replace('/', '_') + '.fatemp'
        with open(tempfile, 'w') as fd:
            fd.write(document.text)

        process = subprocess.Popen(['pep8', tempfile],
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, universal_newlines=True)
        errors, _ = process.communicate(document.text)

        #debug(errors)

        result = []
        for match in ERROR_REGEX.findall(errors):
            if match == None:
                raise Exception('Error doesn\'t match error format')
            else:
                line = int(match[1]) - 1 # Our line numbering starts with 0
                column = int(match[2]) - 1 # Our column numbering starts with 0
                message = match[3]
                beg = coord_to_position(line, column, document.text)
                result.append(('error', Interval(beg, beg + 1), message))
        return result


errorchecker = Pep8Checker()
