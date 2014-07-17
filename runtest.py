#!python3
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-r', '--rerun', help='rerun the latest test batch',
        action='store_true')
args = parser.parse_args()

RERUN = args.rerun

import os
import sys
from unittest import defaultTestLoader as loader, TextTestRunner

path_to_fate = os.path.dirname(os.path.abspath(__file__)) + '/../'
sys.path.insert(0, path_to_fate)

suite = loader.discover('fate')
runner = TextTestRunner()
runner.run(suite)
