from unittest import TestCase
from ..navigation import (move_n_wrapped_lines_down, move_n_wrapped_lines_up,
                          beg_of_wrapped_line)


class TestNavigation(TestCase):

    def test_beg_of_wrapped_line(self):
        f = beg_of_wrapped_line
        text = '123\n123\n123\n'

        for start in range(12):
            assert f(text, 10, start) == 4 * (start // 4)
            assert f(text, 4, start) == 4 * (start // 4)
            assert f(text, 2, start) == 2 * (start // 2)
            assert f(text, 1, start) == start

    def test_move_n_wrapped_lines_down(self):
        f = move_n_wrapped_lines_down
        text = '123\n123\n123\n'

        for start in range(12):
            for n in range(5):
                assert f(text, 10, start, n) == min(4 * (start // 4 + n), 12)
                assert f(text, 4, start, n) == min(4 * (start // 4 + n), 12)

        for i in range(3):
            assert f(text, 2, 0, i) == 2 * i

        for i in range(6):
            assert f(text, 1, 0, i) == i

        text = '\n\n\n'
        for i in range(4):
            assert f(text, 10, 0, i) == i

    def test_move_n_wrapped_lines_up(self):
        return
        text = '123\n123\n123\nx'
        l = len(text) - 1
        assert move_n_wrapped_lines_up(text, 10, l, 0) == l - 0
        assert move_n_wrapped_lines_up(text, 10, l, 1) == l - 4
        assert move_n_wrapped_lines_up(text, 10, l, 2) == l - 8
        assert move_n_wrapped_lines_up(text, 10, l, 3) == l - 12
        assert move_n_wrapped_lines_up(text, 10, l, 4) == l - 12

        text = '\n\n\n'
        l = len(text) - 1
        assert move_n_wrapped_lines_up(text, 10, l, 0) == l - 0
        assert move_n_wrapped_lines_up(text, 10, l, 1) == l - 1
        assert move_n_wrapped_lines_up(text, 10, l, 2) == l - 2
