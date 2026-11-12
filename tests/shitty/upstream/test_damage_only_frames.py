# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


class DamageOnlyFrameTest(unittest.TestCase):
    def test_resize_between_failed_present_and_retry_rebuilds_full_frame(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"before")
            before = terminal.snapshot()
            terminal.fail_next_present()
            terminal.write(b"+failed")
            self.assertEqual(terminal.snapshot(), before)

            terminal.resize(5, 3)
            retried = terminal.snapshot()
            self.assertEqual((retried.columns, retried.rows), (5, 3))
            self.assertEqual(retried.lines, ["befor", "e+fai", "led  "])
            self.assertEqual(retried.refresh_count, before.refresh_count + 1)

    def test_cursor_only_change_publishes_without_cell_damage(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"abcd")
            before = terminal.snapshot()
            terminal.write(b"\x1b[2D")
            after = terminal.snapshot()

            self.assertEqual(after.cells, before.cells)
            self.assertEqual((after.cursor_x, after.cursor_y), (2, 0))
            self.assertEqual(after.refresh_count, before.refresh_count + 1)

    def test_selection_only_change_publishes_without_cell_damage(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"selection")
            terminal.select_start(0, 0)
            before = terminal.snapshot()
            terminal.select_update(3, 0)
            after = terminal.snapshot()

            self.assertEqual(after.cells, before.cells)
            self.assertNotEqual(after.selection, before.selection)
            self.assertEqual(after.refresh_count, before.refresh_count + 1)


if __name__ == "__main__":
    unittest.main()
