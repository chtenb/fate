from unittest import TestCase, main
from .. import actions
from ..session import Session
from random import choice
from ..command import publics, call_action
from tempfile import gettempdir
from sys import path
from os import urandom
import random
from ..runtest import RERUN

# importing RandomizedUserInterface will take care of creating a userinterface
from . import randomized_userinterface

TEXT = """\n
import sys

class Foo(Bar):
    def __init__(self):
        pass
        pass

    def start(self):
        print('Start!')
        return 1
"""

action_dict = publics(actions)
action_names = list(action_dict.keys())

class RandomizedActionTest(TestCase):
    def setUp(self):
        self.session = Session()
        self.session.text = TEXT

    def test_actions(self):
        if RERUN:
            path.insert(0, gettempdir())
            try:
                from last_test_batch_fate import seed, batch
            except ImportError:
                raise Exception('Can\'t rerun batch: no previous batch exists.')
            else:
                self.run_batch(seed, batch)
        else:
            for run in range(10):
                print('Run ' + str(run + 1))
                seed = urandom(10)
                batch = [self.get_random_action() for _ in range(100)]
                self.run_batch(seed, batch)

    def run_batch(self, seed, batch):
        path = gettempdir() + '/last_test_batch_fate.py'
        print('Saving run into ' + path)

        with open(path, 'w') as f:
            f.write('seed = {}\n'.format(seed))
            f.write('batch = {}\n'.format(batch))

        random.seed(seed)
        for i, name in enumerate(batch):
            print(str(i + 1) + ': executing ' + name)
            call_action(action_dict[name], self.session)

        #print('Result:\n' + self.session.text)

    def get_random_action(self):
        while 1:
            name = choice(action_names)
            if name != 'quit_session':
                break
        return name

if __name__ == '__main__':
    main()
