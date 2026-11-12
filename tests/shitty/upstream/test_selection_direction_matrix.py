# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty, put_rows


ROWS = (b"abcdef", b"ghijkl", b"mnopqr")


class SelectionDirectionMatrixTest(unittest.TestCase):
    def test_linear_reverse_drag_matches_forward_drag(self):
        results = []
        for start, end in (((1, 0), (4, 2)), ((4, 2), (1, 0))):
            with Shitty(columns=6, rows=3) as terminal:
                terminal.write(put_rows(*ROWS))
                terminal.select_start(*start)
                terminal.select_update(*end)
                results.append(terminal.select_finish())
        self.assertEqual(results, [b"bcdef\nghijkl\nmnop", b"bcdef\nghijkl\nmnop"])

    def test_rectangular_drag_is_direction_independent(self):
        directions = (
            ((1, 0), (4, 2)),
            ((4, 2), (1, 0)),
            ((4, 0), (1, 2)),
            ((1, 2), (4, 0)),
        )
        for start, end in directions:
            with self.subTest(start=start, end=end):
                with Shitty(columns=6, rows=3) as terminal:
                    terminal.write(put_rows(*ROWS))
                    terminal.select_start(*start)
                    terminal.select_rectangular()
                    terminal.select_update(*end)
                    self.assertEqual(terminal.select_finish(), b"bcd\nhij\nnop")

    def test_enabling_rectangle_normalizes_cross_row_linear_corners(self):
        with Shitty(columns=6, rows=3) as terminal:
            terminal.write(put_rows(*ROWS))
            terminal.select_start(4, 0)
            terminal.select_update(1, 2)
            terminal.select_rectangular()
            self.assertEqual(terminal.select_finish(), b"bcd\nhij\nnop")

    def test_rectangle_keeps_anchor_when_enabled_during_reverse_x_drag(self):
        with Shitty(columns=6, rows=3) as terminal:
            terminal.write(put_rows(*ROWS))
            terminal.select_start(4, 0)
            terminal.select_update(1, 2)
            terminal.select_rectangular()
            terminal.select_update(3, 2)
            self.assertEqual(terminal.select_finish(), b"d\nj\np")

    def test_drag_can_cross_both_axes_repeatedly(self):
        with Shitty(columns=6, rows=3) as terminal:
            terminal.write(put_rows(*ROWS))
            terminal.select_start(3, 1)
            terminal.select_rectangular()
            terminal.select_update(1, 0)
            terminal.select_update(5, 2)
            terminal.select_update(2, 0)
            self.assertEqual(terminal.select_finish(), b"c\ni")


if __name__ == "__main__":
    unittest.main()
