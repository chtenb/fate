import random
import os
from tempfile import gettempdir
from .basetestcase import BaseTestCase
from .. import commands
from ..commandmode import publics
from ..commandtools import execute
from .randomizeduserinterface import RandomizedUserSimulator
from .testargs import args

command_dict = publics(commands)
command_names = list(command_dict.keys())
# Sorting is needed to be able to reproduce a seeded random test case
command_names.sort()


class RandomizedActionTest(BaseTestCase):

    def setUp(self):
        #from ..runtest import args
        self.args = args

        self.create_userinterface = RandomizedUserSimulator
        BaseTestCase.setUp(self)
        self.runs, self.commands_per_run = (5000, 50) if args.long else (500, 50)

    def test_random_commands(self):
        if self.args.no_randomized_tests:
            print('Skipping randomized tests')
            return

        if self.args.seed != None:
            self.run_seeded_testcase(int(self.args.seed))
        elif self.args.rerun:
            self.run_last_testcase()
        else:
            self.run_new_testcases()

    def run_last_testcase(self):
        """Rerun last testcase based on seed."""
        try:
            with open(gettempdir() + '/last_test_seed_fate.tmp') as f:
                seed = int(f.read())
        except IOError:
            raise Exception('Can\'t rerun testcase: no previous testcase exists.')
        else:
            self.run_seeded_testcase(seed)

    def run_new_testcases(self):
        """Run newly generated testcases."""
        for run in range(self.runs):
            # Make sure to create a new document for each run
            self.setUp()

            # Generate a new seed
            seed = int.from_bytes(os.urandom(10), byteorder='big')
            random.seed(seed)

            print('Run {} (seed={})'.format(run + 1, seed))

            self.run_seeded_testcase(seed)

    def run_seeded_testcase(self, seed):
        """Run a testcase based on given seed."""
        savefile = gettempdir() + '/last_test_seed_fate.tmp'
        if self.args.verbose:
            print('Saving run into ' + savefile)
        with open(savefile, 'w') as f:
            f.write(str(seed))

        random.seed(seed)
        testcase = [self.get_random_command() for _ in range(self.commands_per_run)]
        self.run_testcase(testcase)

    def run_testcase(self, testcase):
        """Run the given testcase."""
        if self.args.verbose:
            print('Sample text:\n' + str(self.document.text))
            print('Starting selection: ' + str(self.document.selection))

        for i, name in enumerate(testcase):
            if self.args.verbose:
                print(str(i + 1) + ': executing ' + name)
            execute(command_dict[name], self.document)

    def get_random_command(self):
        while 1:
            name = random.choice(command_names)
            if name not in ['quit_document', 'force_quit', 'open_document']:
                break
        return name
