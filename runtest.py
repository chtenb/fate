import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-r', '--rerun', help='rerun the latest test batch',
                    command='store_true')
parser.add_argument('-l', '--long', help='start a long testing document',
                    command='store_true')
parser.add_argument('-n', '--no-randomized-tests',
                    help='don \'t run the randomized tests', command='store_true')
parser.add_argument('-v', '--verbose', help='run in verbose mode',
                    command='store_true')
args = parser.parse_args()

import os
import sys
from unittest import defaultTestLoader as loader, TextTestRunner

path_to_fate = os.path.dirname(os.path.abspath(__file__)) + '/../'
sys.path.insert(0, path_to_fate)

suite = loader.discover('fate')
runner = TextTestRunner()
test_result = runner.run(suite)
success = test_result.wasSuccessful()
if not success:
    sys.exit(1)
