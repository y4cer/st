# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


class ResizeMarginsTabsTest(unittest.TestCase):
    def test_resize_resets_vertical_margins_to_new_screen(self):
        with Shitty(columns=8, rows=5) as terminal:
            terminal.write(b"\x1b[2;4r\x1b[?6h")
            terminal.resize(8, 6)
            terminal.write(b"\x1b[HX")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(0, 0).char, "X")
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 0))

    def test_resize_resets_horizontal_margins_to_new_screen(self):
        with Shitty(columns=8, rows=4) as terminal:
            terminal.write(b"\x1b[?69h\x1b[3;6s\x1b[?6h")
            terminal.resize(7, 4)
            terminal.write(b"\x1b[HX")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(0, 0).char, "X")
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 0))

    def test_default_tab_stops_follow_grown_and_shrunk_width(self):
        with Shitty(columns=7, rows=2) as terminal:
            terminal.resize(10, 2)
            terminal.write(b"\x1b[H\tX")
            self.assertEqual(terminal.snapshot().cell(8, 0).char, "X")
            terminal.resize(6, 2)
            terminal.write(b"\x1b[H\tY")
            self.assertEqual(terminal.snapshot().cell(5, 0).char, "Y")

    def test_out_of_range_custom_tab_is_clamped_after_shrink(self):
        with Shitty(columns=12, rows=2) as terminal:
            terminal.write(b"\x1b[1;10H\x1bH\x1b[H")
            terminal.resize(6, 2)
            terminal.write(b"\tX")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(5, 0).char, "X")
            self.assertEqual(snapshot.cursor_x, 5)

    def test_in_range_custom_tabs_survive_shrink_and_grow(self):
        with Shitty(columns=10, rows=2) as terminal:
            terminal.write(b"\x1b[3g\x1b[1;4H\x1bH\x1b[H")
            terminal.resize(6, 2)
            terminal.resize(12, 2)
            terminal.write(b"\tX")
            self.assertEqual(terminal.snapshot().cell(3, 0).char, "X")

    def test_cbt_never_crosses_left_margin_with_default_tabs(self):
        with Shitty(columns=12, rows=3) as terminal:
            terminal.write(b"\x1b[?69h\x1b[3;9s\x1b[?6h\x1b[1;8H\x1b[Z")
            self.assertEqual(terminal.snapshot().cursor_x, 2)

    def test_custom_forward_and_backward_tabs_stay_inside_margins(self):
        with Shitty(columns=12, rows=3) as terminal:
            terminal.write(
                b"\x1b[3g\x1b[1;2H\x1bH\x1b[1;5H\x1bH"
                b"\x1b[?69h\x1b[3;9s\x1b[?6h\x1b[1;8H\x1b[2Z"
            )
            self.assertEqual(terminal.snapshot().cursor_x, 2)


if __name__ == "__main__":
    unittest.main()
