# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


def assert_wide_cells_are_complete(test, snapshot):
    for row in range(snapshot.rows):
        for column in range(snapshot.columns):
            cell = snapshot.cell(column, row)
            if cell.double_width:
                test.assertLess(column + 1, snapshot.columns)
                test.assertTrue(
                    snapshot.cell(
                        column + 1,
                        row,
                    ).double_width_continuation
                )
            if cell.double_width_continuation:
                test.assertGreater(column, 0)
                test.assertTrue(
                    snapshot.cell(column - 1, row).double_width
                )


class GhosttyDeleteCharsTest(unittest.TestCase):
    def test_count_clips_to_the_editing_region_and_damages_the_row(self):
        cases = (
            (b"\x1b[2P", "ADE  "),
            (b"\x1b[3P", "AE   "),
            (b"\x1b[10P", "A    "),
            (b"\x1b[P", "ACDE "),
        )
        for operation, expected in cases:
            with self.subTest(operation=operation), Shitty(
                columns=5,
                rows=2,
            ) as terminal:
                terminal.write(b"ABCDE\x1b[1;2H" + operation)
                self.assertEqual(terminal.snapshot().lines[0], expected)
                self.assertEqual(terminal.last_update_rows(), (0,))

        with Shitty(columns=10, rows=2) as terminal:
            terminal.write(b"ABC123\x1b[1;3H\x1b[2P")
            self.assertEqual(terminal.snapshot().lines[0], "AB23      ")

    def test_zero_parameter_is_the_protocol_default_of_one(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"ABCDE\x1b[1;2H\x1b[0P")
            self.assertEqual(terminal.snapshot().lines[0], "ACDE ")

    def test_delete_clears_pending_wrap_and_the_soft_wrap_marker(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"ABCDE")
            self.assertTrue(terminal.cursor_pending_wrap())
            terminal.write(b"\x1b[P")
            self.assertFalse(terminal.cursor_pending_wrap())
            terminal.write(b"X")
            self.assertEqual(terminal.snapshot().lines[0], "ABCDX")

        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"ABCDE123")
            self.assertTrue(terminal.model_snapshot().cell(4, 0).wrapped)
            terminal.write(b"\x1b[1;1H\x1b[PX")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines, ["XCDE ", "123  "])
            self.assertFalse(snapshot.cell(4, 0).wrapped)

    def test_erased_tail_uses_current_colors_without_visual_attributes(self):
        with Shitty(columns=10, rows=2) as terminal:
            terminal.write(
                b"ABC123\x1b[1;3H"
                b"\x1b[1;3;4:3;7;38;2;12;34;56;48;2;255;0;0m"
                b"\x1b[2P"
            )
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[0], "AB23      ")
            for column in (8, 9):
                cell = snapshot.cell(column, 0)
                self.assertEqual(cell.foreground, (12, 34, 56))
                self.assertEqual(cell.background, (255, 0, 0))
                self.assertFalse(
                    cell.bold
                    or cell.italic
                    or cell.underline
                    or cell.inverse
                )

    def test_horizontal_margins_bound_deletion_but_vertical_margins_do_not(self):
        with Shitty(columns=6, rows=3) as terminal:
            terminal.write(
                b"ABC123"
                b"\x1b[?69h\x1b[3;5s"
                b"\x1b[1;4H\x1b[P"
            )
            self.assertEqual(terminal.snapshot().lines[0], "ABC2 3")

        with Shitty(columns=6, rows=3) as terminal:
            terminal.write(
                b"ABC123"
                b"\x1b[?69h\x1b[3;5s"
                b"\x1b[1;6H"
            )
            terminal.snapshot()
            terminal.write(b"\x1b[2P")
            self.assertFalse(terminal.cursor_pending_wrap())
            self.assertEqual(terminal.last_update(), (0, 0))
            self.assertEqual(terminal.snapshot().lines[0], "ABC123")

        with Shitty(columns=6, rows=4) as terminal:
            terminal.write(
                b"ABC123"
                b"\x1b[2;3r"
                b"\x1b[1;1H\x1b[99P"
            )
            self.assertEqual(terminal.snapshot().lines[0], "      ")

    def test_delete_repairs_each_local_wide_character_boundary(self):
        cases = (
            (
                b"A" + "橋".encode() + b"123\x1b[1;3H\x1b[P",
                "A 123 ",
            ),
            (
                "橋123".encode() + b"\x1b[1;1H\x1b[P",
                " 123  ",
            ),
            (
                b"A" + "橋".encode() + b"123\x1b[1;1H\x1b[P",
                "橋 123 ",
            ),
        )
        for stream, expected in cases:
            with self.subTest(expected=expected), Shitty(
                columns=6,
                rows=2,
            ) as terminal:
                terminal.write(stream)
                snapshot = terminal.model_snapshot()
                self.assertEqual(snapshot.lines[0], expected)
                assert_wide_cells_are_complete(self, snapshot)

    def test_delete_removes_pre_wrap_marker_shifted_from_the_right_edge(self):
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write(
                b"0123"
                + "橋".encode()
                + b"123"
                + b"\x1b[1;1H\x1b[P"
            )
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[0], "123  ")
            self.assertFalse(snapshot.cell(4, 0).wrapped)
            assert_wide_cells_are_complete(self, snapshot)

    def test_delete_discards_every_orphan_at_a_wide_wrap_boundary(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(
                "😀a😀b😀".encode()
                + b"\x1b[1;2H\x1b[3P"
            )
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[0], "  b😀    ")
            assert_wide_cells_are_complete(self, snapshot)

        with Shitty(columns=8, rows=3) as terminal:
            terminal.write(
                b"......."
                + "😀".encode()
                + b"abcde"
                + "😀".encode()
                + b"......"
                + b"\x1b[2;2H\x1b[3P"
            )
            snapshot = terminal.model_snapshot()
            self.assertEqual(
                snapshot.lines,
                ["....... ", " cde    ", "😀 ......"],
            )
            self.assertTrue(
                any(snapshot.cell(column, 0).wrapped for column in range(8))
            )
            self.assertFalse(
                any(snapshot.cell(column, 1).wrapped for column in range(8))
            )
            assert_wide_cells_are_complete(self, snapshot)

    def test_delete_clears_a_wide_glyph_straddling_the_right_margin(self):
        with Shitty(columns=8, rows=3) as terminal:
            terminal.write(
                b"123456"
                + "橋".encode()
                + b"\x1b[?69h\x1b[2;7s"
                + b"\x1b[1;2H\x1b[P"
            )
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[0], "13456   ")
            assert_wide_cells_are_complete(self, snapshot)


if __name__ == "__main__":
    unittest.main()
