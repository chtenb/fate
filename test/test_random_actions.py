from unittest import main
from .basetestcase import BaseTestCase
from .. import actions
from random import choice
from ..command import publics
from ..actiontools import execute
from tempfile import gettempdir
from sys import path
from os import urandom
import random
from ..runtest import args
from .randomized_userinterface import RandomizedUserSimulator

action_dict = publics(actions)
action_names = list(action_dict.keys())

class RandomizedActionTest(BaseTestCase):
    def setUp(self):
        self.UserInterfaceClass = RandomizedUserSimulator
        BaseTestCase.setUp(self)

    def test_random_actions(self):
        if args.no_randomized_tests:
            print('Skipping randomized tests')
        else:
            if args.rerun:
                path.insert(0, gettempdir())
                try:
                    from last_test_batch_fate import seed, batch
                except ImportError:
                    raise Exception('Can\'t rerun batch: no previous batch exists.')
                else:
                    self.run_batch(seed, batch)
            else:
                runs, actions = (5000, 50) if args.long else (500, 50)
                for run in range(runs):
                    print('Run ' + str(run + 1))

                    # Make sure to create a new document for each run
                    self.setUp()
                    seed = urandom(10)
                    batch = [self.get_random_action() for _ in range(actions)]

                    self.run_batch(seed, batch)

    def run_batch(self, seed, batch):
        savefile = gettempdir() + '/last_test_batch_fate.py'

        if args.verbose:
            print('Saving run into ' + savefile)
            print('Seed: ' + str(seed))
            print('Text:\n' + str(self.document.text))
            print('Selection: ' + str(self.document.selection))

        with open(savefile, 'w') as f:
            f.write('seed = {}\n'.format(seed))
            f.write('batch = {}\n'.format(batch))

        random.seed(seed)
        for i, name in enumerate(batch):
            if args.verbose:
                print(str(i + 1) + ': executing ' + name)
            execute(action_dict[name], self.document)

        #print('Result:\n' + self.document.text)

    def get_random_action(self):
        while 1:
            name = choice(action_names)
            if name not in ['quit_document', 'force_quit']:
                break
        return name

