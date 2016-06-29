"""
Script for running the tests.
"""
import sys
import traceback
import argparse

from unittest import defaultTestLoader, TextTestRunner

import fate
import fate_logger
from fate.test import cmdargs

parser = argparse.ArgumentParser()
parser.add_argument('-r', '--rerun', help='rerun the latest testcase',
                    action='store_true')
parser.add_argument('-s', '--seed', help='run a testcase with given seed',
                    action='store')
parser.add_argument('-l', '--long', help='start a long testing session',
                    action='store_true')
parser.add_argument('-n', '--no-randomized-tests',
                    help='don \'t run the randomized tests', action='store_true')
parser.add_argument('-v', '--verbose', help='run in verbose mode',
                    action='store_true')
parser.add_argument('-m', '--module', help='run single module',
                    action='store')
parser.add_argument('-p', '--print-logs', help='write log messages to stdout',
                    action='store_true')
parser.add_argument('-f', '--failfast', help='fail after first error',
                    action='store_true')
parser.add_argument('-d', '--debug', help='run the test suite without collecting results',
                    action='store_true')
args = parser.parse_args()
cmdargs.args = args
fate_logger.LOG_TO_STDOUT = args.print_logs

# Dump locals on exception
def excepthook(type, value, tb):
    traceback.print_exception(type, value, tb)

    while tb.tb_next:
        tb = tb.tb_next

    print('Locals:',  tb.tb_frame.f_locals, file=sys.stderr)

sys.excepthook = excepthook

if args.module:
    module = 'fate.' + args.module
    print('Loading ' + module)
    suite = defaultTestLoader.loadTestsFromName(module)
else:
    suite = defaultTestLoader.discover('.')

if args.debug:
    suite.debug()
else:
    # TODO: tb_locals is not always supported. Find out when it is supported and make that a
    # requirements.
    runner = TextTestRunner(failfast=args.failfast, tb_locals=args.verbose)
    test_result = runner.run(suite)

    success = test_result.wasSuccessful()
    if not success:
        sys.exit(1)
