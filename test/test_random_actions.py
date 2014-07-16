from unittest import TestCase, main
from .. import actions
from ..session import Session
from random import choice
from ..command import publics, call_action

# importing RandomizedUserInterface will take care of creating a userinterface
from . import randomized_userinterface

TEXT = """\
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

    def get_random_action(self):
        while 1:
            name = choice(action_names)
            if name != 'quit_session':
                break
        return name, action_dict[name]

    def test_actions(self):
        for run in range(10):
            print('Run ' + str(run + 1))
            for i in range(100):
                name, action = self.get_random_action()
                print(str(i + 1) + ': executing ' + name)
                call_action(action, self.session)
            print('Result: ')
            print(self.session.text)
if __name__ == '__main__':
    main()
