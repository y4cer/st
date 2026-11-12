# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty, put_rows


class GhosttyEraseDisplayTest(unittest.TestCase):
    def test_below_above_and_complete_have_exact_damage(self):
        cases = (
            (
                b"\x1b[J",
                ["ABC  ", "D    ", "     ", "     ", "     "],
                (1, 2, 3, 4),
            ),
            (
                b"\x1b[1J",
                ["     ", "  F  ", "GHI  ", "     ", "     "],
                (0, 1),
            ),
            (
                b"\x1b[2J",
                ["     ", "     ", "     ", "     ", "     "],
                (0, 1, 2, 3, 4),
            ),
        )
        for operation, expected, damaged_rows in cases:
            with self.subTest(operation=operation), Shitty(
                columns=5,
                rows=5,
            ) as terminal:
                terminal.write(
                    put_rows(b"ABC", b"DEF", b"GHI")
                    + b"\x1b[2;2H"
                )
                terminal.write(operation)
                snapshot = terminal.snapshot()
                self.assertEqual(snapshot.lines, expected)
                self.assertEqual(
                    (snapshot.cursor_x, snapshot.cursor_y),
                    (1, 1),
                )
                self.assertEqual(
                    terminal.last_update_rows(),
                    damaged_rows,
                )

    def test_each_direction_uses_only_the_current_background(self):
        cases = (
            (
                b"\x1b[J",
                ((1, range(1, 5)), (2, range(5))),
            ),
            (
                b"\x1b[1J",
                ((0, range(5)), (1, range(2))),
            ),
            (
                b"\x1b[2J",
                ((0, range(5)), (1, range(5)), (2, range(5))),
            ),
        )
        for operation, erased in cases:
            with self.subTest(operation=operation), Shitty(
                columns=5,
                rows=3,
            ) as terminal:
                terminal.write(
                    put_rows(b"ABC", b"DEF", b"GHI")
                    + b"\x1b[2;2H"
                    + b"\x1b[1;4:3;7;48;2;255;0;0m"
                    + operation
                )
                snapshot = terminal.model_snapshot()
                for row, columns in erased:
                    for column in columns:
                        cell = snapshot.cell(column, row)
                        self.assertEqual(cell.background, (255, 0, 0))
                        self.assertFalse(
                            cell.bold
                            or cell.underline
                            or cell.inverse
                        )

    def test_below_and_above_remove_both_halves_of_wide_glyphs(self):
        cases = (
            (
                b"\x1b[2;4H\x1b[J",
                ["AB橋 C", "DE   ", "     "],
            ),
            (
                b"\x1b[2;3H\x1b[1J",
                ["     ", "    F", "GH橋 I"],
            ),
        )
        for operation, expected in cases:
            with self.subTest(operation=operation), Shitty(
                columns=5,
                rows=3,
            ) as terminal:
                terminal.write(
                    put_rows(
                        "AB橋C".encode(),
                        "DE橋F".encode(),
                        "GH橋I".encode(),
                    )
                    + operation
                )
                snapshot = terminal.model_snapshot()
                self.assertEqual(snapshot.lines, expected)
                for row in range(snapshot.rows):
                    for column in range(snapshot.columns):
                        cell = snapshot.cell(column, row)
                        if cell.double_width:
                            self.assertLess(column + 1, snapshot.columns)
                            self.assertTrue(
                                snapshot.cell(
                                    column + 1,
                                    row,
                                ).double_width_continuation
                            )
                        if cell.double_width_continuation:
                            self.assertGreater(column, 0)
                            self.assertTrue(
                                snapshot.cell(
                                    column - 1,
                                    row,
                                ).double_width
                            )

    def test_regular_ed_respects_iso_but_not_dec_protection(self):
        cases = (
            (b"\x1b[J", ["ABC  ", "D    ", "     "]),
            (b"\x1b[1J", ["     ", "  F  ", "GHI  "]),
            (b"\x1b[2J", ["     ", "     ", "     "]),
        )
        for operation, erased_result in cases:
            with self.subTest(protection="ISO", operation=operation), Shitty(
                columns=5,
                rows=3,
            ) as terminal:
                terminal.write(
                    b"\x1bV"
                    + put_rows(b"ABC", b"DEF", b"GHI")
                    + b"\x1bW\x1b[2;2H"
                    + operation
                )
                self.assertEqual(
                    terminal.snapshot().lines,
                    ["ABC  ", "DEF  ", "GHI  "],
                )

            with self.subTest(protection="DEC", operation=operation), Shitty(
                columns=5,
                rows=3,
            ) as terminal:
                terminal.write(
                    b"\x1b[1\"q"
                    + put_rows(b"ABC", b"DEF", b"GHI")
                    + b"\x1b[0\"q\x1b[2;2H"
                    + operation
                )
                self.assertEqual(
                    terminal.snapshot().lines,
                    erased_result,
                )

    def test_toggling_dec_protection_does_not_destroy_iso_protection(self):
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write(
                b"\x1bV"
                + put_rows(b"ABC", b"DEF", b"GHI")
                + b"\x1bW"
                b"\x1b[1\"q\x1b[0\"q"
                b"\x1b[2;2H\x1b[2J"
            )
            self.assertEqual(
                terminal.snapshot().lines,
                ["ABC  ", "DEF  ", "GHI  "],
            )

    def test_selective_ed_respects_dec_protection_in_every_direction(self):
        cases = (
            (b"\x1b[2;4H\x1b[?J", ["A         ", "123  X    "]),
            (b"\x1b[2;8H\x1b[?1J", ["          ", "     X  9 "]),
            (b"\x1b[2;4H\x1b[?2J", ["          ", "     X    "]),
        )
        for operation, expected_prefix in cases:
            with self.subTest(operation=operation), Shitty(
                columns=10,
                rows=5,
            ) as terminal:
                terminal.write(
                    put_rows(b"A", b"123456789")
                    + b"\x1b[2;6H\x1b[1\"qX\x1b[0\"q"
                    + operation
                )
                snapshot = terminal.model_snapshot()
                self.assertEqual(
                    snapshot.lines[:2],
                    expected_prefix,
                )
                self.assertTrue(snapshot.cell(5, 1).protected)

    def test_selective_ed_does_not_treat_iso_protection_as_decsca(self):
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write(
                b"\x1bV"
                + put_rows(b"ABC", b"DEF", b"GHI")
                + b"\x1bW\x1b[2;2H\x1b[?2J"
            )
            self.assertEqual(terminal.snapshot().lines, ["     "] * 3)

    def test_complete_erase_preserves_cursor_and_current_pen(self):
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(
                b"\x1b[1;3;4;38;2;7;8;9m"
                b"AAAA"
                b"\x1b[3;4H"
            )
            before = terminal.pen_state()
            terminal.write(b"\x1b[2J")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["     "] * 5)
            self.assertEqual(
                (snapshot.cursor_x, snapshot.cursor_y),
                (3, 2),
            )
            self.assertEqual(terminal.pen_state(), before)

    def test_erase_saved_lines_discards_only_scrollback(self):
        with Shitty(columns=8, rows=3, save_lines=8) as terminal:
            terminal.write(b"one\r\ntwo\r\nthree\r\nfour")
            live = terminal.snapshot().lines
            terminal.write(b"\x1b[3J")
            self.assertEqual(terminal.snapshot().lines, live)
            terminal.page_up()
            self.assertEqual(terminal.snapshot().view_offset, 0)


if __name__ == "__main__":
    unittest.main()
