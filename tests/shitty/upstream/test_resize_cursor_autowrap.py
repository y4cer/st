# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty, put_rows


class ResizeCursorAutowrapTest(unittest.TestCase):
    def test_height_shrink_scrolls_only_enough_to_keep_cursor_visible(self):
        with Shitty(columns=5, rows=5, save_lines=8) as terminal:
            terminal.write(put_rows(b"A", b"B", b"C", b"D", b"E"))
            terminal.write(b"\x1b[4;1H")
            terminal.resize(5, 2)
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["C    ", "D    "])
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 1))

    def test_grow_restores_rows_scrolled_only_for_cursor_visibility(self):
        with Shitty(columns=5, rows=5, save_lines=8) as terminal:
            terminal.write(put_rows(b"A", b"B", b"C", b"D", b"E"))
            terminal.write(b"\x1b[4;1H")
            terminal.resize(5, 2)
            terminal.resize(5, 5)
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[:4], ["A    ", "B    ", "C    ", "D    "])
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 3))

    def test_height_shrink_does_not_scroll_when_cursor_already_fits(self):
        with Shitty(columns=5, rows=5, save_lines=8) as terminal:
            terminal.write(put_rows(b"A", b"B", b"C", b"D", b"E"))
            terminal.write(b"\x1b[2;2H")
            terminal.resize(5, 2)
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["A    ", "B    "])
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 1))

    def test_width_shrink_reflows_pending_wrap(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"abcde")
            terminal.resize(3, 2)
            terminal.write(b"X")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["abc", "deX"])
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (2, 1))

    def test_width_grow_clears_obsolete_pending_wrap(self):
        with Shitty(columns=3, rows=2) as terminal:
            terminal.write(b"abc")
            terminal.resize(5, 2)
            terminal.write(b"X")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["abcX ", "     "])
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (4, 0))


if __name__ == "__main__":
    unittest.main()
