from .. import ErrorChecker
from tempfile import gettempdir
import subprocess
import re
from ...selection import Interval
from ...navigation import coord_to_position

from logging import debug

ERROR_REGEX = re.compile(r'(?s)File "(.+)", line (\d+).*\^\s*(\w+: .+)\n')


class PythonChecker(ErrorChecker):

    name = 'python'

    def __init__(self):
        pass

    def check(self, document):
        tempfile = gettempdir() + '/' + document.filename.replace('/', '_') + '.fatemp'
        with open(tempfile, 'w') as fd:
            fd.write(document.text)

        process = subprocess.Popen(['python3', '-B', '-mpy_compile', tempfile],
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, universal_newlines=True)
        _, errors = process.communicate(document.text)

        #debug(errors)

        result = []
        for match in ERROR_REGEX.findall(errors):
            if match == None:
                raise Exception('Error doesn\'t match error format')
            else:
                line = int(match[1]) - 1 # Our line numbering starts with 0
                message = match[2]
                print(line)
                print(repr(document.text))
                beg = coord_to_position(line, 0, document.text)
                try:
                    end = coord_to_position(line + 1, 0, document.text) - 1
                except ValueError:
                    end = len(document.text)
                result.append(('error', Interval(beg, end), message))
        return result


errorchecker = PythonChecker()
