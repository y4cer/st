# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


class ResizeTest(unittest.TestCase):
    def test_growing_reflows_cells_and_cursor(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"abcde123")
            terminal.resize(7, 3)
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.columns, snapshot.rows), (7, 3))
            self.assertEqual(snapshot.lines, ["abcde12", "3      ", "       "])
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 1))
            self.assertEqual(terminal.winsize(), (7, 3))

    def test_shrinking_reflows_cells_and_cursor_into_history(self):
        with Shitty(columns=7, rows=3, save_lines=4) as terminal:
            terminal.write(b"abcde\r\n12345")
            terminal.resize(4, 2)
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["1234", "5   "])
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 1))
            terminal.wheel_up(4)
            self.assertEqual(terminal.snapshot().lines, ["abcd", "e   "])

    def test_resize_alternate_screen_and_restore_primary(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"main\x1b[?1049halt")
            terminal.resize(7, 3)
            terminal.write(b"\x1b[?1049l")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.columns, snapshot.rows), (7, 3))
            self.assertEqual(snapshot.lines[0], "main   ")

    def test_initial_pty_winsize_matches_grid(self):
        with Shitty(columns=11, rows=7) as terminal:
            self.assertEqual(terminal.winsize(), (11, 7))

    def test_pty_winsize_includes_grid_pixels(self):
        with Shitty(columns=11, rows=7, glyph_px=8, glyph_py=16) as terminal:
            self.assertEqual(
                terminal.winsize_full(),
                (11, 7, 88, 112),
            )
            terminal.resize(13, 9)
            self.assertEqual(
                terminal.winsize_full(),
                (13, 9, 104, 144),
            )

    def test_resize_across_compact_screen_boundary(self):
        # Crossing 255 columns/rows switches the screen implementation to
        # wider coordinate types; content, history, cursor and scrollback
        # must survive the conversion in both directions.
        with Shitty(columns=80, rows=24, save_lines=100) as terminal:
            terminal.write(b"history-line\r\n" * 30)
            terminal.write(b"tail")
            terminal.resize(300, 260)
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.columns, snapshot.rows), (300, 260))
            self.assertEqual(snapshot.lines[snapshot.cursor_y].rstrip(), "tail")
            self.assertEqual(snapshot.lines[snapshot.cursor_y - 1].rstrip(), "history-line")
            terminal.resize(80, 24)
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.columns, snapshot.rows), (80, 24))
            self.assertEqual(snapshot.lines[snapshot.cursor_y].rstrip(), "tail")
            terminal.wheel_up(24)
            self.assertEqual(terminal.snapshot().lines[0].rstrip(), "history-line")

    def test_large_screen_damage_and_history(self):
        with Shitty(columns=300, rows=260, save_lines=50000) as terminal:
            terminal.write(b"\x1b[260;300H")
            terminal.write(b"x")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[259][299], "x")
            terminal.write(b"\r\nscrolled")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[259][:8], "scrolled")
            self.assertEqual(snapshot.lines[258][299], "x")
            terminal.wheel_up(1)
            self.assertEqual(terminal.snapshot().lines[259][299], "x")


    def test_a_resize_ends_synchronized_output(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(b"\x1b[?2026hab")
            terminal.resize(12, 5)
            terminal.write(b"\x1b[?2026$p")
            self.assertEqual(terminal.read_input(), b"\x1b[?2026;2$y")
            self.assertEqual(terminal.snapshot().lines[0].rstrip(), "ab")


if __name__ == "__main__":
    unittest.main()
