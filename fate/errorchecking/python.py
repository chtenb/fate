from . import ErrorChecker
from tempfile import gettempdir
import subprocess
import re
from ..selection import Interval

from logging import info


def coord_to_position(line, column, text):
    position = 0
    while line:
        position = text.find('\n', position + 1)
        line -= 1
    return position + column


class PythonChecker(ErrorChecker):
    def __init__(self):
        pass

    def run(self, document):
        tempfile = gettempdir() + '/' + document.filename + '.fatemp'
        with open(tempfile, 'w') as fd:
            fd.write(document.text)

        process = subprocess.Popen(['python3', '-B', '-mpy_compile', tempfile],
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, universal_newlines=True)
        _, errors = process.communicate(document.text)

        error_regex = re.compile(r'File "(.+)", line (\d+).*\^\s*(\w+: .+)', re.DOTALL)

        info(errors)

        result = {}
        for match in error_regex.findall(errors):
            if match == None:
                raise Exception('Error doesn\'t match error format')
            else:
                line = int(match[1])
                message = match[2]
                pos = coord_to_position(line, 0, document.text) - 1
                result[pos] = 'error'
        info(result)
        return result


errorchecker = PythonChecker()

