# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


class ResizeReflowTest(unittest.TestCase):
    def test_soft_wrapped_line_reflows_narrower_and_wider(self):
        with Shitty(columns=10, rows=4, save_lines=8) as terminal:
            terminal.write(b"ABCDEFGHI")
            terminal.resize(6, 4)
            narrow = terminal.snapshot()
            self.assertEqual(narrow.lines[:2], ["ABCDEF", "GHI   "])
            self.assertTrue(narrow.cell(5, 0).wrapped)
            self.assertEqual((narrow.cursor_x, narrow.cursor_y), (3, 1))

            terminal.resize(12, 4)
            wide = terminal.snapshot()
            self.assertEqual(wide.lines[:2], ["ABCDEFGHI   ", "            "])
            self.assertFalse(any(cell.wrapped for cell in wide.cells[:12]))
            self.assertEqual((wide.cursor_x, wide.cursor_y), (9, 0))

    def test_hard_line_breaks_are_not_joined(self):
        with Shitty(columns=6, rows=3) as terminal:
            terminal.write(b"abc\r\ndef")
            terminal.resize(12, 3)
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[:2], ["abc         ", "def         "])
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (3, 1))

    def test_reflow_keeps_wide_graphemes_intact(self):
        cluster = "👩\N{ZERO WIDTH JOINER}💻"
        with Shitty(columns=5, rows=3, save_lines=4) as terminal:
            terminal.write(("abc" + cluster + "z").encode())
            terminal.resize(4, 3)
            narrow = terminal.snapshot()
            self.assertEqual(narrow.lines[:2], ["abc ", "👩 z "])
            self.assertTrue(narrow.cell(0, 1).double_width)
            self.assertTrue(narrow.cell(1, 1).double_width_continuation)
            self.assertFalse(narrow.cell(3, 0).double_width)
            terminal.select_start(0, 1)
            terminal.select_update(2, 1)
            self.assertEqual(terminal.select_finish(), cluster.encode())

            terminal.resize(8, 3)
            wide = terminal.snapshot()
            self.assertEqual(wide.lines[0], "abc👩 z  ")
            self.assertTrue(wide.cell(3, 0).double_width)
            self.assertTrue(wide.cell(4, 0).double_width_continuation)

    def test_reflow_uses_scrollback_and_preserves_bottom_anchor(self):
        with Shitty(columns=6, rows=3, save_lines=8) as terminal:
            terminal.write(b"ABCDEFGHIJKL\r\nhard")
            terminal.resize(4, 3)
            bottom = terminal.snapshot()
            self.assertEqual(bottom.lines, ["EFGH", "IJKL", "hard"])
            terminal.wheel_up(1)
            history = terminal.snapshot()
            self.assertEqual(history.lines, ["ABCD", "EFGH", "IJKL"])
            terminal.wheel_down(8)

            terminal.resize(12, 3)
            wide = terminal.snapshot()
            self.assertEqual(wide.lines[:2], ["ABCDEFGHIJKL", "hard        "])

    def test_linear_selection_tracks_reflowed_cells(self):
        with Shitty(columns=6, rows=3, save_lines=4) as terminal:
            terminal.write(b"ABCDEFGHI")
            terminal.select_start(2, 0)
            terminal.select_update(3, 1)

            terminal.resize(4, 3)

            self.assertEqual(terminal.select_finish(), b"CDEFGHI")

    def test_inactive_primary_screen_reflows_on_restore(self):
        with Shitty(columns=5, rows=3, save_lines=4) as terminal:
            terminal.write(b"ABCDE123")
            terminal.write(b"\x1b[?47h")
            terminal.resize(8, 3)
            terminal.write(b"\x1b[?47l")

            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0], "ABCDE123")
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (7, 0))

    def test_mode_1049_restores_reflowed_primary_cursor(self):
        with Shitty(columns=5, rows=3, save_lines=4) as terminal:
            terminal.write(b"ABCDE123")
            terminal.write(b"\x1b[?1049h")
            terminal.resize(8, 3)
            terminal.write(b"\x1b[?1049l")

            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0], "ABCDE123")
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (7, 0))

    def test_scrolled_view_tracks_the_same_soft_wrapped_text(self):
        with Shitty(columns=6, rows=3, save_lines=8) as terminal:
            terminal.write(b"ABCDEFGHIJKL\r\nhard\r\nlast")
            terminal.wheel_up(1)
            self.assertEqual(terminal.snapshot().lines[0], "ABCDEF")

            terminal.resize(4, 3)

            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["ABCD", "EFGH", "IJKL"])
            self.assertEqual(snapshot.view_offset, 2)


if __name__ == "__main__":
    unittest.main()
