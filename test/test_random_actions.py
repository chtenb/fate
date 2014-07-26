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
from ..runtest import RERUN, LONG, NO_RANDOMIZED_TESTS
from .randomized_userinterface import RandomizedUserSimulator

action_dict = publics(actions)
action_names = list(action_dict.keys())

class RandomizedActionTest(BaseTestCase):
    def setUp(self):
        self.UserInterfaceClass = RandomizedUserSimulator
        BaseTestCase.setUp(self)

    def test_random_actions(self):
        if NO_RANDOMIZED_TESTS:
            print('Skipping randomized tests')
        else:
            if RERUN:
                path.insert(0, gettempdir())
                try:
                    from last_test_batch_fate import seed, batch
                except ImportError:
                    raise Exception('Can\'t rerun batch: no previous batch exists.')
                else:
                    self.run_batch(seed, batch)
            else:
                runs, actions = (1000, 200) if LONG else (100, 100)
                for run in range(runs):
                    print('Run ' + str(run + 1))

                    # Make sure to create a new session for each run
                    self.setUp()
                    seed = urandom(10)
                    batch = [self.get_random_action() for _ in range(actions)]

                    self.run_batch(seed, batch)

    def run_batch(self, seed, batch):
        savefile = gettempdir() + '/last_test_batch_fate.py'

        print('Saving run into ' + savefile)
        print('Seed: ' + str(seed))
        print('Text:\n' + str(self.session.text))
        print('Selection: ' + str(self.session.selection))

        with open(savefile, 'w') as f:
            f.write('seed = {}\n'.format(seed))
            f.write('batch = {}\n'.format(batch))

        random.seed(seed)
        for i, name in enumerate(batch):
            print(str(i + 1) + ': executing ' + name)
            execute(action_dict[name], self.session)

        #print('Result:\n' + self.session.text)

    def get_random_action(self):
        while 1:
            name = choice(action_names)
            if name != 'quit_session':
                break
        return name

if __name__ == '__main__':
    main()
