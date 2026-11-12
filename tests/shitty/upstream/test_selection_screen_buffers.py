# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


class SelectionScreenBuffersTest(unittest.TestCase):
    def test_primary_selection_survives_mode_47_round_trip(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"primary")
            terminal.select_start(0, 0)
            terminal.select_update(4, 0)
            terminal.write(b"\x1b[?47halt\x1b[?47l")
            self.assertEqual(terminal.select_finish(), b"prim")

    def test_primary_and_alternate_selections_are_independent(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"primary\x1b[?47h\x1b[Hsecond")
            terminal.select_start(0, 0)
            terminal.select_update(3, 0)
            self.assertEqual(terminal.select_finish(), b"sec")
            terminal.write(b"\x1b[?47l")
            terminal.select_start(0, 0)
            terminal.select_update(4, 0)
            self.assertEqual(terminal.select_finish(), b"prim")
            terminal.write(b"\x1b[?47h")
            self.assertEqual(terminal.select_finish(), b"sec")

    def test_mode_1047_clears_only_alternate_selection_and_contents(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"primary")
            terminal.select_start(0, 0)
            terminal.select_update(4, 0)
            terminal.write(b"\x1b[?47h\x1b[Halt")
            terminal.select_start(0, 0)
            terminal.select_update(3, 0)
            terminal.write(b"\x1b[?1047l")
            self.assertEqual(terminal.select_finish(), b"prim")
            terminal.write(b"\x1b[?47h")
            self.assertEqual(terminal.select_finish(), b"")
            self.assertEqual(terminal.snapshot().lines[0], "        ")

    def test_mode_1049_preserves_primary_selection_while_alt_is_temporary(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"primary")
            terminal.select_start(1, 0)
            terminal.select_update(5, 0)
            terminal.write(b"\x1b[?1049halt\x1b[?1049l")
            self.assertEqual(terminal.select_finish(), b"rima")

    def test_snapshot_exposes_only_active_screen_selection(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"primary")
            terminal.select_start(1, 0)
            terminal.select_update(5, 0)
            self.assertEqual(terminal.snapshot().selection, (1, 0, 5, 0))
            terminal.write(b"\x1b[?47h")
            self.assertEqual(terminal.snapshot().selection, (-1, -1, -1, -1))
            terminal.write(b"\x1b[?47l")
            self.assertEqual(terminal.snapshot().selection, (1, 0, 5, 0))


if __name__ == "__main__":
    unittest.main()
