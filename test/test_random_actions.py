from unittest import TestCase, main
from ..session import Session
from .. import actions
from random import choice
from logging import debug

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

action_names = list(vars(actions).keys())

class RandomTest(TestCase):
    def setUp(self):
        self.session = Session()
        self.session.text = TEXT

    def get_random_action(self):
        name = choice(action_names)
        debug(name)
        return vars(actions)[name]

    def test_actions(self):
        for _ in range(100):
            result = self.get_random_action()
            while callable(result):
                result = result(self.session)

if __name__ == '__main__':
    main()
