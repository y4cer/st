# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


class ResizeHistoryCapacityTest(unittest.TestCase):
    def test_repeated_shrink_grow_does_not_duplicate_history(self):
        with Shitty(columns=5, rows=4, save_lines=3) as terminal:
            terminal.write(b"1\r\n2\r\n3\r\n4\r\n5\r\n6")
            for _ in range(4):
                terminal.resize(5, 2)
                terminal.resize(5, 4)
            terminal.page_up()
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.view_offset, 1)
            self.assertEqual(snapshot.lines, ["2    ", "3    ", "4    ", "5    "])

    def test_capacity_keeps_only_newest_rows_after_resize_cycles(self):
        with Shitty(columns=5, rows=3, save_lines=2) as terminal:
            terminal.write(b"1\r\n2\r\n3\r\n4\r\n5\r\n6")
            for _ in range(3):
                terminal.resize(5, 1)
                terminal.resize(5, 3)
            terminal.write(b"\r\n7\r\n8\r\n9")
            terminal.wheel_up(10)
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.view_offset, 2)
            self.assertEqual(snapshot.lines, ["5    ", "6    ", "7    "])

    def test_active_alternate_resize_keeps_cursor_rows_without_history(self):
        with Shitty(columns=5, rows=3, save_lines=3) as terminal:
            terminal.write(
                b"\x1b[?47h\x1b[?1007l\x1b[H1\r\n2\r\n3\r\n4\r\n5"
            )
            terminal.resize(5, 2)
            terminal.resize(5, 4)
            terminal.resize(5, 2)
            terminal.wheel_up(10)
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.view_offset, 0)
            self.assertEqual(snapshot.lines, ["4    ", "5    "])

    def test_inactive_alternate_buffer_survives_primary_resize(self):
        with Shitty(columns=6, rows=3, save_lines=2) as terminal:
            terminal.write(b"\x1b[?47h\x1b[HALT\x1b[?47l")
            terminal.resize(8, 4)
            terminal.write(b"\x1b[?47h")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0], "ALT     ")
            self.assertEqual((snapshot.columns, snapshot.rows), (8, 4))


if __name__ == "__main__":
    unittest.main()
