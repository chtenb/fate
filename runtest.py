import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-r', '--rerun', help='rerun the latest test batch',
                    action='store_true')
parser.add_argument('-l', '--long', help='start a long testing session',
                    action='store_true')
parser.add_argument('-n', '--no-randomized-tests',
                    help='don \'t run the randomized tests', action='store_true')
parser.add_argument('-v', '--verbose', help='run in verbose mode',
                    action='store_true')
parser.add_argument('-m', '--module', help='run single module',
                    action='store')
args = parser.parse_args()
print(args.module)

import os
import sys
from unittest import defaultTestLoader as loader, TextTestRunner

path_to_fate = os.path.dirname(os.path.abspath(__file__)) + '/../'
sys.path.insert(0, path_to_fate)

if args.module:
    suite = loader.loadTestsFromName('fate.' + args.module)
else:
    suite = loader.discover('fate')

runner = TextTestRunner()
result = runner.run(suite)
success = result.wasSuccessful()
if not success:
    sys.exit(1)
