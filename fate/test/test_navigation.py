from unittest import TestCase
from ..navigation import (move_n_wrapped_lines_down, move_n_wrapped_lines_up,
                          beg_of_wrapped_line)


class TestNavigation(TestCase):

    def test_beg_of_wrapped_line(self):
        f = beg_of_wrapped_line
        text = '123\n123\n123\n'

        for start in range(12):
            assert f(text, 8, start) == 4 * (start // 4)
            assert f(text, 4, start) == 4 * (start // 4)
            assert f(text, 2, start) == 2 * (start // 2)
            assert f(text, 1, start) == start

        text = '\n\n\n'
        for start in range(3):
            assert f(text, 8, start) == start

        text = '123'
        for start in range(3):
            assert f(text, 8, start) == 0

    def test_move_n_wrapped_lines_down(self):
        f = move_n_wrapped_lines_down

        text = '123\n123\n123\n'
        for start in range(12):
            for n in range(14):
                assert f(text, 8, start, n) == min(4 * (start // 4 + n), 8)
                assert f(text, 4, start, n) == min(4 * (start // 4 + n), 8)
                assert f(text, 2, start, n) == min(2 * (start // 2 + n), 10)
                assert f(text, 1, start, n) == min(start + n, 11)

        text = '\n\n\n'
        for start in range(3):
            for n in range(5):
                assert f(text, 8, start, n) == min(start + n, 2)

        text = '123'
        for start in range(3):
            for n in range(5):
                assert f(text, 8, start, n) == 0

    def test_move_n_wrapped_lines_up(self):
        f = move_n_wrapped_lines_up

        text = '123\n123\n123\n'
        l = len(text)
        for start in range(12):
            for n in range(14):
                assert f(text, 8, start, n) == max(4 * (start // 4 - n), 0)
                assert f(text, 4, start, n) == max(4 * (start // 4 - n), 0)
                assert f(text, 2, start, n) == max(2 * (start // 2 - n), 0)
                assert f(text, 1, start, n) == max(start - n, 0)

        text = '\n\n\n'
        for start in range(3):
            for n in range(5):
                assert f(text, 8, start, n) == max(start - n, 0)


        text = '123'
        for start in range(3):
            for n in range(5):
                assert f(text, 8, start, n) == 0

