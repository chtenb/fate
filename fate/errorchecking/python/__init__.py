from .python import PythonChecker
from .pep8 import Pep8Checker

errorcheckers = [Pep8Checker(), PythonChecker()]
