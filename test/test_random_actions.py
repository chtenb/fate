import random
import os
from tempfile import gettempdir
from .basetestcase import BaseTestCase
from random import choice
from ..commandtools import execute
from tempfile import gettempdir
from os import urandom
import random
from .randomized_userinterface import RandomizedUserSimulator
from .cmdargs import args


class RandomizedActionTest(BaseTestCase):

    def setUp(self):
        self.args = args

        self.create_userinterface = RandomizedUserSimulator
        BaseTestCase.setUp(self)

    def test_random_commands(self):
        if self.args.no_randomized_tests:
            print('Skipping randomized tests')
            return

        runs, commands_per_run = (5000, 50) if args.long else (500, 50)
        seed = self.getseed()

        # Save seed into temp file
        savefile = gettempdir() + '/last_test_seed_fate.tmp'
        if self.args.verbose:
            print('Saving run into ' + savefile)
        with open(savefile, 'w') as f:
            f.write(str(seed))

        self.run_test(seed, commands_per_run)

    def getseed(self):
        if args.seed != None:
            return int(args.seed)

        if args.rerun:
            self.run_last_testcase()
            try:
                with open(gettempdir() + '/last_test_seed_fate.tmp') as f:
                    seed = int(f.read())
                    return seed
            except IOError:
                raise Exception('Can\'t rerun testcase: no previous testcase exists.')
            self.run_new_testcases()

        # Generate a new seed
        seed = int.from_bytes(urandom(10), byteorder='big')
        random.seed(seed)

    def run_test(self, seed, commands_per_run):
        """Run the test based on given seed."""
        if args.verbose:
            print('Sample text:\n' + str(self.document.text))
            print('Starting selection: ' + str(self.document.selection))

        random.seed(seed)
        run = 1
        print('Run {} (seed={})'.format(run + 1, seed))

        for i in range(commands_per_run):
            userinput = self.document.ui.getinput()

            # If the cancel key has been pressed, convert input to Cancel
            if userinput == self.document.cancelkey:
                userinput = 'Cancel'

            if args.verbose:
                try:
                    name = userinput.__name__
                except AttributeError:
                    name = str(userinput)
                print(str(i + 1) + ': Input = ' + name)

            if self.document.mode:
                # We are not in normalmode
                self.document.mode[-1].processinput(self.document, userinput)
            else:
                # We are in normalmode
                if type(userinput) == str:
                    key = userinput
                    if key in self.document.keymap:
                        command = self.document.keymap[key]
                    else:
                        command = None
                else:
                    command = userinput

                while callable(command):
                    command = command(self.document)
