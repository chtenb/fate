from unittest import TestCase, main
from .. import actions
from . import randomized_userinterface
from ..session import Session
from random import choice
from ..command import publics, call_action

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
        print('Executing ' + name)
        return action_dict[name]

    def test_actions(self):
        for _ in range(100):
            action = self.get_random_action()
            call_action(action, self.session)

if __name__ == '__main__':
    main()
