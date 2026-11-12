# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Public adaptations of xterm.js InputHandler cases 61 through 80."""

import unittest

from harness import Shitty


UPSTREAM_CASES = (
    "colon notation: CSI 38:5:50 m",
    "colon notation: CSI 38:5: m",
    "colon notation: CSI 38;5:50 m",
    "early sequence end: CSI 38:2 m",
    "early sequence end: CSI 38:5 m",
    "surrounding attrs: CSI 1;38:2::50:100:150;4 m",
    "surrounding attrs: CSI 1;38:2::50:100:;4 m",
    "surrounding attrs: CSI 1;38:2::50:100;4 m",
    "surrounding attrs: CSI 1;38:2::;4 m",
    "surrounding attrs: CSI 1;38;2::;4 m",
    "cursor forward (CUF)",
    "cursor backward (CUB)",
    "cursor down (CUD)",
    "cursor up (CUU)",
    "cursor next line (CNL)",
    "cursor previous line (CPL)",
    "cursor character absolute (CHA)",
    "cursor position (CUP)",
    "cursor position (CUP) with DECOM and scroll margins",
    "horizontal position absolute (HPA)",
)


def cursor(terminal):
    snapshot = terminal.snapshot()
    return snapshot.cursor_x, snapshot.cursor_y


def assert_rgb_with_surrounding_attrs(test, sequence, expected):
    with Shitty(columns=10, rows=10) as terminal:
        terminal.write(sequence)
        pen = terminal.pen_state()
        test.assertTrue(pen.bold)
        test.assertTrue(pen.underline)
        test.assertEqual(pen.foreground, expected)


class XtermJsInputHandlerCursorTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 20)
        self.assertEqual(len(set(UPSTREAM_CASES)), 20)

    def test_colon_palette_index_matches_semicolon_form(self):
        with Shitty(columns=10, rows=10) as terminal:
            terminal.write(b"\x1b[38:5:50m")
            self.assertEqual(terminal.pen_state().foreground_index, 50)

    def test_colon_palette_missing_index_defaults_to_zero(self):
        with Shitty(columns=10, rows=10) as terminal:
            terminal.write(b"\x1b[38;5;99m\x1b[38:5:m")
            self.assertEqual(terminal.pen_state().foreground_index, 0)

    def test_mixed_semicolon_palette_selector_and_colon_index(self):
        with Shitty(columns=10, rows=10) as terminal:
            terminal.write(b"\x1b[38;5:50m")
            self.assertEqual(terminal.pen_state().foreground_index, 50)

    @unittest.expectedFailure
    def test_colon_rgb_early_end_defaults_every_component_to_zero(self):
        with Shitty(columns=10, rows=10) as terminal:
            terminal.write(b"\x1b[38;2;1;2;3m\x1b[38:2m")
            self.assertEqual(terminal.pen_state().foreground, (0, 0, 0))

    @unittest.expectedFailure
    def test_colon_palette_early_end_defaults_index_to_zero(self):
        with Shitty(columns=10, rows=10) as terminal:
            terminal.write(b"\x1b[38;5;99m\x1b[38:5m")
            self.assertEqual(terminal.pen_state().foreground_index, 0)

    def test_complete_colon_rgb_preserves_leading_and_following_attrs(self):
        assert_rgb_with_surrounding_attrs(
            self, b"\x1b[1;38:2::50:100:150;4m", (50, 100, 150)
        )

    def test_missing_blue_colon_rgb_preserves_surrounding_attrs(self):
        assert_rgb_with_surrounding_attrs(
            self, b"\x1b[1;38:2::50:100:;4m", (50, 100, 0)
        )

    @unittest.expectedFailure
    def test_early_colon_rgb_end_preserves_following_underline(self):
        assert_rgb_with_surrounding_attrs(
            self, b"\x1b[1;38:2::50:100;4m", (50, 100, 0)
        )

    @unittest.expectedFailure
    def test_empty_colon_rgb_preserves_surrounding_attrs(self):
        assert_rgb_with_surrounding_attrs(
            self, b"\x1b[1;38:2::;4m", (0, 0, 0)
        )

    @unittest.expectedFailure
    def test_mixed_empty_rgb_preserves_surrounding_attrs(self):
        assert_rgb_with_surrounding_attrs(
            self, b"\x1b[1;38;2::;4m", (0, 0, 0)
        )

    def test_cursor_forward_defaults_clamps_and_preserves_row(self):
        with Shitty(columns=10, rows=10) as terminal:
            for sequence, expected in (
                (b"\x1b[C", (1, 0)),
                (b"\x1b[1C", (2, 0)),
                (b"\x1b[4C", (6, 0)),
                (b"\x1b[100C", (9, 0)),
                (b"\x1b[5;9H\x1b[C", (9, 4)),
            ):
                terminal.write(sequence)
                self.assertEqual(cursor(terminal), expected)

    def test_cursor_backward_defaults_clamps_and_preserves_row(self):
        with Shitty(columns=10, rows=10) as terminal:
            for sequence, expected in (
                (b"\x1b[D", (0, 0)),
                (b"\x1b[1D", (0, 0)),
                (b"\x1b[100C\x1b[D", (8, 0)),
                (b"\x1b[1D", (7, 0)),
                (b"\x1b[4D", (3, 0)),
                (b"\x1b[100D", (0, 0)),
                (b"\x1b[5;5H\x1b[D", (3, 4)),
            ):
                terminal.write(sequence)
                self.assertEqual(cursor(terminal), expected)

    def test_cursor_down_defaults_clamps_and_preserves_column(self):
        with Shitty(columns=10, rows=10) as terminal:
            for sequence, expected in (
                (b"\x1b[B", (0, 1)),
                (b"\x1b[1B", (0, 2)),
                (b"\x1b[4B", (0, 6)),
                (b"\x1b[100B", (0, 9)),
                (b"\x1b[1;9H\x1b[B", (8, 1)),
            ):
                terminal.write(sequence)
                self.assertEqual(cursor(terminal), expected)

    def test_cursor_up_defaults_clamps_and_preserves_column(self):
        with Shitty(columns=10, rows=10) as terminal:
            for sequence, expected in (
                (b"\x1b[A", (0, 0)),
                (b"\x1b[1A", (0, 0)),
                (b"\x1b[100B\x1b[A", (0, 8)),
                (b"\x1b[1A", (0, 7)),
                (b"\x1b[4A", (0, 3)),
                (b"\x1b[100A", (0, 0)),
                (b"\x1b[10;9H\x1b[A", (8, 8)),
            ):
                terminal.write(sequence)
                self.assertEqual(cursor(terminal), expected)

    def test_cursor_next_line_defaults_clamps_and_resets_column(self):
        with Shitty(columns=10, rows=10) as terminal:
            for sequence, expected in (
                (b"\x1b[E", (0, 1)),
                (b"\x1b[1E", (0, 2)),
                (b"\x1b[4E", (0, 6)),
                (b"\x1b[100E", (0, 9)),
                (b"\x1b[1;9H\x1b[E", (0, 1)),
            ):
                terminal.write(sequence)
                self.assertEqual(cursor(terminal), expected)

    def test_cursor_previous_line_defaults_clamps_and_resets_column(self):
        with Shitty(columns=10, rows=10) as terminal:
            for sequence, expected in (
                (b"\x1b[F", (0, 0)),
                (b"\x1b[1F", (0, 0)),
                (b"\x1b[100E\x1b[F", (0, 8)),
                (b"\x1b[1F", (0, 7)),
                (b"\x1b[4F", (0, 3)),
                (b"\x1b[100F", (0, 0)),
                (b"\x1b[10;9H\x1b[F", (0, 8)),
            ):
                terminal.write(sequence)
                self.assertEqual(cursor(terminal), expected)

    def test_cursor_character_absolute_defaults_and_clamps(self):
        with Shitty(columns=10, rows=10) as terminal:
            for sequence, expected in (
                (b"\x1b[G", (0, 0)),
                (b"\x1b[1G", (0, 0)),
                (b"\x1b[2G", (1, 0)),
                (b"\x1b[5G", (4, 0)),
                (b"\x1b[100G", (9, 0)),
            ):
                terminal.write(sequence)
                self.assertEqual(cursor(terminal), expected)

    def test_cursor_position_defaults_omissions_and_clamps(self):
        with Shitty(columns=10, rows=10) as terminal:
            for sequence, expected in (
                (b"\x1b[6;6H\x1b[H", (0, 0)),
                (b"\x1b[6;6H\x1b[1H", (0, 0)),
                (b"\x1b[6;6H\x1b[1;1H", (0, 0)),
                (b"\x1b[6;6H\x1b[8H", (0, 7)),
                (b"\x1b[6;6H\x1b[;8H", (7, 0)),
                (b"\x1b[6;6H\x1b[100;100H", (9, 9)),
            ):
                terminal.write(sequence)
                self.assertEqual(cursor(terminal), expected)

    def test_cursor_position_is_relative_to_decom_scroll_margins(self):
        with Shitty(columns=10, rows=10) as terminal:
            terminal.write(b"\x1b[?6h\x1b[2;3r\x1b[1;1H")
            self.assertEqual(cursor(terminal), (0, 1))
            terminal.write(b"X")
            self.assertEqual(terminal.snapshot().cell(0, 1).char, "X")
            terminal.write(b"\x1b[2;1H")
            self.assertEqual(cursor(terminal), (0, 2))
            terminal.write(b"\x1b[10;10H")
            self.assertEqual(cursor(terminal), (9, 2))
            terminal.write(b"\x1b[?6l\x1b[2;1H")
            self.assertEqual(cursor(terminal), (0, 1))

    def test_horizontal_position_absolute_defaults_and_clamps(self):
        with Shitty(columns=10, rows=10) as terminal:
            for sequence, expected in (
                (b"\x1b[`", (0, 0)),
                (b"\x1b[1`", (0, 0)),
                (b"\x1b[2`", (1, 0)),
                (b"\x1b[5`", (4, 0)),
                (b"\x1b[100`", (9, 0)),
            ):
                terminal.write(sequence)
                self.assertEqual(cursor(terminal), expected)


if __name__ == "__main__":
    unittest.main()
