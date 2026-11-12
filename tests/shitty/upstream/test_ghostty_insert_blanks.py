# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


def assert_wide_cells_are_complete(test, snapshot, row=0):
    for column in range(snapshot.columns):
        cell = snapshot.cell(column, row)
        if cell.double_width:
            test.assertLess(column + 1, snapshot.columns)
            test.assertTrue(
                snapshot.cell(column + 1, row).double_width_continuation
            )
        if cell.double_width_continuation:
            test.assertGreater(column, 0)
            test.assertTrue(snapshot.cell(column - 1, row).double_width)


class GhosttyInsertBlanksTest(unittest.TestCase):
    def test_basic_count_clipping_and_damage(self):
        cases = (
            (5, b"ABC\x1b[1;1H\x1b[2@", "  ABC"),
            (3, b"ABC\x1b[1;1H\x1b[2@", "  A"),
            (3, b"ABC\x1b[1;1H\x1b[5@", "   "),
            (5, b"  ABC\x1b[1;3H\x1b[2@X", "  X A"),
        )
        for columns, stream, expected in cases:
            with self.subTest(columns=columns, stream=stream), Shitty(
                columns=columns,
                rows=2,
            ) as terminal:
                terminal.write(stream)
                self.assertEqual(terminal.snapshot().lines[0], expected)
                self.assertEqual(terminal.last_update_rows(), (0,))

    def test_zero_parameter_is_the_protocol_default_of_one(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"ABC\x1b[1;1H\x1b[0@")
            self.assertEqual(terminal.snapshot().lines[0], " ABC ")

    def test_inserted_cells_use_erase_colors_without_visual_attributes(self):
        with Shitty(columns=6, rows=2) as terminal:
            terminal.write(
                b"ABCDEF\x1b[1;1H"
                b"\x1b[1;3;4:3;7;38;2;12;34;56;48;2;255;0;0m"
                b"\x1b[2@"
            )
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[0], "  ABCD")
            for column in (0, 1):
                cell = snapshot.cell(column, 0)
                self.assertEqual(cell.foreground, (12, 34, 56))
                self.assertEqual(cell.background, (255, 0, 0))
                self.assertFalse(
                    cell.bold
                    or cell.italic
                    or cell.underline
                    or cell.inverse
                )

    def test_horizontal_margins_limit_insert_and_outside_is_a_noop(self):
        with Shitty(columns=10, rows=2) as terminal:
            terminal.write(
                b"\x1b[3GABC"
                b"\x1b[?69h\x1b[3;5s"
                b"\x1b[1;3H\x1b[2@X"
            )
            self.assertEqual(terminal.snapshot().lines[0], "  X A     ")

        with Shitty(columns=6, rows=2) as terminal:
            terminal.write(
                b"\x1b[?69h\x1b[2;4s"
                b"\x1b[1;5HAB"
            )
            self.assertTrue(terminal.cursor_pending_wrap())
            terminal.write(b"\x1b[2@")
            self.assertFalse(terminal.cursor_pending_wrap())
            self.assertEqual(terminal.snapshot().lines[0], "    AB")
            self.assertEqual(terminal.last_update(), (0, 0))

    def test_large_count_clears_only_the_horizontal_region(self):
        with Shitty(columns=10, rows=2) as terminal:
            terminal.write(
                b"abcdefghij"
                b"\x1b[?69h\x1b[3;5s"
                b"\x1b[1;3H\x1b[140@"
            )
            self.assertEqual(terminal.snapshot().lines[0], "ab   fghij")

    def test_insert_repairs_every_wide_character_boundary(self):
        cases = (
            (
                b"123" + "橋".encode() + b"\x1b[1;1H\x1b[@",
                " 123 ",
            ),
            (
                "橋123".encode() + b"\x1b[1;2H\x1b[@",
                "   12",
            ),
            (
                b"ABCD" + "橋".encode()
                + b"\x1b[?69h\x1b[1;5s\x1b[1;3H\x1b[@",
                "AB CD     ",
            ),
            (
                "中中中中中".encode()
                + b"\x1b[?69h\x1b[1;9s"
                + b"a\x1b[8@",
                "a         ",
            ),
        )
        for stream, expected in cases:
            with self.subTest(expected=expected), Shitty(
                columns=len(expected),
                rows=2,
            ) as terminal:
                terminal.write(stream)
                snapshot = terminal.model_snapshot()
                self.assertEqual(snapshot.lines[0], expected)
                assert_wide_cells_are_complete(self, snapshot)

    def test_grapheme_payload_is_shifted_or_dropped_atomically(self):
        family = "👨‍👩‍👧"
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(
                b"A" + family.encode() + b"\x1b[1;1H\x1b[@"
            )
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[0], " A👨  ")
            self.assertEqual(
                snapshot.cell(2, 0).grapheme,
                tuple(map(ord, family)),
            )

        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(
                b"ABC" + family.encode() + b"\x1b[1;1H\x1b[4@"
            )
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[0], "    A")
            self.assertTrue(all(not cell.grapheme for cell in snapshot.cells))

    def test_hyperlink_moves_with_text_and_not_with_inserted_blanks(self):
        with Shitty(columns=10, rows=2) as terminal:
            terminal.write(
                b"\x1b]8;;https://example.com\x1b\\"
                b"ABC"
                b"\x1b]8;;\x1b\\"
                b"\x1b[1;1H\x1b[2@"
            )
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[0], "  ABC     ")
            for column in range(10):
                linked = 2 <= column < 5
                self.assertEqual(bool(snapshot.cell(column, 0).hyperlink), linked)
                self.assertEqual(
                    terminal.hyperlink(column, 0),
                    "https://example.com" if linked else "",
                )

        with Shitty(columns=3, rows=2) as terminal:
            terminal.write(
                b"\x1b]8;;https://example.com\x1b\\"
                b"ABC"
                b"\x1b]8;;\x1b\\"
                b"\x1b[1;1H\x1b[3@"
            )
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[0], "   ")
            self.assertTrue(all(not cell.hyperlink for cell in snapshot.cells))

    def test_insert_mode_shifts_narrow_and_wide_input_without_wrapping_tail(self):
        cases = (
            (10, b"hello\x1b[1;2H\x1b[4hX", "hXello    "),
            (5, b"hello\x1b[1;2H\x1b[4hX", "hXell"),
            (5, b"hello\x1b[4hX", "hello", "X    "),
            (
                5,
                b"hello\x1b[1;2H\x1b[4h" + "😀".encode(),
                "h😀 el",
            ),
            (5, b"well\x1b[4h" + "😀".encode(), "well ", "😀    "),
            (
                5,
                b"123" + "😀".encode() + b"\x1b[1;1H\x1b[4hX",
                "X123 ",
            ),
        )
        for case in cases:
            columns, stream, *expected = case
            with self.subTest(stream=stream), Shitty(
                columns=columns,
                rows=2,
            ) as terminal:
                terminal.write(stream)
                snapshot = terminal.model_snapshot()
                self.assertEqual(snapshot.lines[: len(expected)], expected)
                for row in range(snapshot.rows):
                    assert_wide_cells_are_complete(self, snapshot, row)


if __name__ == "__main__":
    unittest.main()
