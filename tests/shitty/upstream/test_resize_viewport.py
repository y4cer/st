# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


def populate(terminal):
    terminal.write(b"1\r\n2\r\n3\r\n4\r\n5\r\n6")


class ResizeViewportTest(unittest.TestCase):
    def test_width_resize_preserves_view_offset_and_top_row(self):
        with Shitty(columns=5, rows=3, save_lines=6) as terminal:
            populate(terminal)
            terminal.wheel_up(2)
            before = terminal.snapshot()
            terminal.resize(8, 3)
            after = terminal.snapshot()
            self.assertEqual(before.view_offset, 2)
            self.assertEqual(after.view_offset, 2)
            self.assertEqual(after.lines, ["2       ", "3       ", "4       "])

    def test_height_shrink_keeps_scrolled_view_anchored(self):
        with Shitty(columns=5, rows=3, save_lines=6) as terminal:
            populate(terminal)
            terminal.wheel_up(2)
            terminal.resize(5, 2)
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.view_offset, 3)
            self.assertEqual(snapshot.lines, ["2    ", "3    "])

    def test_height_grow_keeps_same_top_row_when_possible(self):
        with Shitty(columns=5, rows=3, save_lines=6) as terminal:
            populate(terminal)
            terminal.wheel_up(2)
            terminal.resize(5, 2)
            terminal.resize(5, 4)
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.view_offset, 1)
            self.assertEqual(snapshot.lines, ["2    ", "3    ", "4    ", "5    "])

    def test_selection_tracks_same_history_text_through_resize(self):
        with Shitty(columns=5, rows=3, save_lines=6) as terminal:
            populate(terminal)
            terminal.wheel_up(2)
            terminal.select_start(0, 0)
            terminal.select_update(1, 0)
            terminal.resize(7, 2)
            self.assertEqual(terminal.select_finish(), b"2")

    def test_output_after_scrolled_resize_does_not_jump_to_bottom(self):
        with Shitty(columns=5, rows=3, save_lines=6) as terminal:
            populate(terminal)
            terminal.wheel_up(2)
            terminal.resize(7, 3)
            terminal.write(b"\r\n7")
            snapshot = terminal.snapshot()
            self.assertGreater(snapshot.view_offset, 0)
            self.assertEqual(snapshot.lines[0].rstrip(), "2")


    def test_a_scrolled_view_survives_growing_and_shrinking(self):
        for geometry, offset, first in (((10, 12), 2, "1"), ((10, 3), 10, "2")):
            with self.subTest(geometry=geometry):
                with Shitty(columns=10, rows=6, save_lines=10) as terminal:
                    terminal.write(
                        b"\r\n".join(str(i).encode() for i in range(1, 15))
                    )
                    terminal.scroll(0, 8)
                    self.assertEqual(terminal.snapshot().view_offset, 8)
                    terminal.resize(*geometry)
                    snapshot = terminal.snapshot()
                    self.assertEqual(snapshot.view_offset, offset)
                    self.assertEqual(snapshot.lines[0].rstrip(), first)


if __name__ == "__main__":
    unittest.main()
