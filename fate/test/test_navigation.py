from unittest import TestCase
from ..navigation import (move_n_wrapped_lines_down, move_n_wrapped_lines_up,
                          beg_of_wrapped_line, end_of_wrapped_line, count_wrapped_lines)
from ..selection import Interval


class TestNavigation(TestCase):

    def test_count_lines(self):
        text = ''
        for width in range(1, 5):
            interval = Interval(0, len(text))
            self.assertEqual(count_wrapped_lines(text, width, interval), 0)

        text = 'x'
        for width in range(1, 5):
            interval = Interval(0, len(text))
            self.assertEqual(count_wrapped_lines(text, width, interval), 1)

        text = '\n\n\n\n'
        for width in range(1, 5):
            interval = Interval(0, len(text))
            self.assertEqual(count_wrapped_lines(text, width, interval), 4)

        text = 'x\nx\nx\nx\n'
        for width in range(1, 5):
            interval = Interval(0, len(text))
            self.assertEqual(count_wrapped_lines(text, width, interval), 4)

        text = 'xyzw\nxyzw\nxyzw\nxyzw\n'
        interval = Interval(0, len(text))
        width = 1
        self.assertEqual(count_wrapped_lines(text, width, interval), 16)
        width = 2
        self.assertEqual(count_wrapped_lines(text, width, interval), 8)
        width = 3
        self.assertEqual(count_wrapped_lines(text, width, interval), 8)
        width = 4
        self.assertEqual(count_wrapped_lines(text, width, interval), 4)

    def test_end_of_wrapped_line(self):
        f = end_of_wrapped_line
        # Parameters: f(text, max_width, start)

        text = ''
        assert f(text, 100, 0) == 0
        assert f(text, 1, 0) == 0

        text = '123\n123\n123\n'
        for start in range(12):
            assert f(text, 8, start) == 4 * (start // 4) + 3
            assert f(text, 4, start) == 4 * (start // 4) + 3
            assert f(text, 2, start) == 2 * (start // 2) + 1
            assert f(text, 1, start) == start

        text = '\n\n\n'
        for start in range(3):
            assert f(text, 8, start) == start

        text = '123'
        for start in range(3):
            assert f(text, 8, start) == 2

        text = '123456789'
        for width in range(1, 12):
            self.assertEqual(f(text, width, 0), min(width, len(text)) - 1)

    def test_beg_of_wrapped_line(self):
        f = beg_of_wrapped_line
        # Parameters: f(text, max_width, start)

        text = ''
        assert f(text, 100, 0) == 0
        assert f(text, 1, 0) == 0

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
        # Parameters: f(text, max_width, start, n)

        text = ''
        assert f(text, 100, 0, 1) == 0
        assert f(text, 1, 0, 1) == 0
        assert f(text, 100, 0, 100) == 0
        assert f(text, 1, 0, 100) == 0

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
        # Parameters: f(text, max_width, start, n)

        text = ''
        assert f(text, 100, 0, 1) == 0
        assert f(text, 1, 0, 1) == 0
        assert f(text, 100, 0, 100) == 0
        assert f(text, 1, 0, 100) == 0

        text = '123\n123\n123\n'
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
