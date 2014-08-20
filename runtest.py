import os
import sys

path_to_fate = os.path.dirname(os.path.abspath(__file__)) + '/../'
sys.path.insert(0, path_to_fate)


import argparse
from fate.test import cmdargs

parser = argparse.ArgumentParser()
parser.add_argument('-r', '--rerun', help='rerun the latest testcase',
                    action='store_true')
parser.add_argument('-s', '--seed', help='run a testcase with given seed',
                    action='store')
parser.add_argument('-l', '--long', help='start a long testing document',
                    action='store_true')
parser.add_argument('-n', '--no-randomized-tests',
                    help='don \'t run the randomized tests', action='store_true')
parser.add_argument('-v', '--verbose', help='run in verbose mode',
                    action='store_true')
parser.add_argument('-m', '--module', help='run single module',
                    action='store')
args = parser.parse_args()
cmdargs.args = args


from unittest import defaultTestLoader as loader, TextTestRunner

if args.module:
    print('Loading fate.' + args.module)
    suite = loader.loadTestsFromName('fate.' + args.module)
else:
    suite = loader.discover('fate')

runner = TextTestRunner()
result = runner.run(suite)
success = result.wasSuccessful()
if not success:
    sys.exit(1)
