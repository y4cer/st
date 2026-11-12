# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


class GhosttySavedCursorTest(unittest.TestCase):
    def test_restore_recovers_rendition_charset_origin_and_protection(self):
        # Asserts bold-brightened palette indices; default off (issue 59).
        with Shitty(
            columns=8, rows=3, extra_arguments=("-boldColors",)
        ) as terminal:
            terminal.write(
                b"\x1b[1;31m"
                b"\x1b(0"
                b"\x1b[1\"q"
                b"\x1b[?6h"
                b"\x1b7"
                b"\x1b[0m"
                b"\x1b(B"
                b"\x1b[0\"q"
                b"\x1b[?6l"
                b"\x1b8q"
            )
            snapshot = terminal.model_snapshot()
            cell = snapshot.cell(0, 0)
            self.assertEqual(cell.char, "─")
            self.assertTrue(cell.bold)
            self.assertTrue(cell.protected)
            self.assertEqual(cell.foreground_index, 9)
            self.assertTrue(terminal.conformance_state()["DECOM"])

    def test_restore_recovers_position_and_pending_wrap(self):
        with Shitty(columns=10, rows=2) as terminal:
            terminal.write(
                b"\x1b[1;5HA\x1b7"
                b"\x1b[1;1HB"
                b"\x1b8X"
            )
            self.assertEqual(terminal.snapshot().lines[0], "B   AX    ")

        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"\x1b[1;5HA")
            self.assertTrue(terminal.cursor_pending_wrap())
            terminal.write(b"\x1b7\x1b[1;1HB\x1b8")
            self.assertTrue(terminal.cursor_pending_wrap())
            terminal.write(b"X")
            self.assertEqual(
                terminal.snapshot().lines,
                ["B   A", "X    "],
            )

    def test_origin_relative_position_uses_the_current_margins_on_restore(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(
                b"\x1b[?6h\x1b7"
                b"\x1b[?69h\x1b[3;5s\x1b[2;4r"
                b"\x1b8X"
            )
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (3, 1))
            self.assertEqual(snapshot.cell(2, 1).char, "X")
            self.assertTrue(terminal.conformance_state()["DECOM"])

    def test_saved_blank_position_tracks_reflow(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(b"\x1b[1;10H\x1b7")
            terminal.resize(5, 5)
            terminal.write(b"\x1b8X")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[1], "    X")
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (4, 1))

    def test_save_and_restore_do_not_own_the_active_hyperlink(self):
        with Shitty(columns=4, rows=2) as terminal:
            terminal.write(
                b"\x1b]8;;https://example.test/saved\x1b\\"
                b"\x1b7A"
                b"\x1b]8;;\x1b\\"
                b"\x1b8\x1b[CB"
            )
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[0], "AB  ")
            self.assertTrue(snapshot.cell(0, 0).hyperlink)
            self.assertFalse(snapshot.cell(1, 0).hyperlink)
            self.assertEqual(
                terminal.hyperlink(0, 0),
                "https://example.test/saved",
            )
            self.assertEqual(terminal.hyperlink(1, 0), "")


if __name__ == "__main__":
    unittest.main()
