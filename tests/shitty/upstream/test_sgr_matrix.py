# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


BASE_PALETTE = (
    (0, 0, 0),
    (170, 0, 0),
    (0, 170, 0),
    (170, 85, 0),
    (0, 0, 170),
    (170, 0, 170),
    (0, 170, 170),
    (170, 170, 170),
    (85, 85, 85),
    (255, 85, 85),
    (85, 255, 85),
    (255, 255, 85),
    (85, 85, 255),
    (255, 85, 255),
    (85, 255, 255),
    (255, 255, 255),
)


class SgrMatrixTest(unittest.TestCase):
    def test_all_ansi_foreground_colors(self):
        with Shitty(columns=16, rows=2) as terminal:
            terminal.write(
                b"".join(
                    f"\x1b[{30 + index if index < 8 else 82 + index}mX".encode()
                    for index in range(16)
                )
            )
            snapshot = terminal.snapshot()

            self.assertEqual(
                [snapshot.cell(column, 0).foreground for column in range(16)],
                list(BASE_PALETTE),
            )

    def test_all_ansi_background_colors(self):
        with Shitty(columns=16, rows=2) as terminal:
            terminal.write(
                b"".join(
                    f"\x1b[{40 + index if index < 8 else 92 + index}mX".encode()
                    for index in range(16)
                )
            )
            snapshot = terminal.snapshot()

            self.assertEqual(
                [snapshot.cell(column, 0).background for column in range(16)],
                list(BASE_PALETTE),
            )

    def test_indexed_color_boundaries_for_all_three_channels(self):
        expected = {
            0: (0, 0, 0),
            7: (170, 170, 170),
            8: (85, 85, 85),
            15: (255, 255, 255),
            16: (0, 0, 0),
            231: (255, 255, 255),
            232: (8, 8, 8),
            255: (238, 238, 238),
        }
        with Shitty(columns=len(expected), rows=2) as terminal:
            terminal.write(
                b"".join(
                    f"\x1b[38;5;{index};48;5;{index};58;5;{index}mX".encode()
                    for index in expected
                )
            )
            snapshot = terminal.snapshot()

            for column, color in enumerate(expected.values()):
                with self.subTest(index=tuple(expected)[column]):
                    cell = snapshot.cell(column, 0)
                    self.assertEqual(cell.foreground, color)
                    self.assertEqual(cell.background, color)
                    self.assertEqual(cell.underline_color, color)

    def test_semicolon_truecolor_minimum_and_maximum(self):
        with Shitty(columns=4, rows=2) as terminal:
            terminal.write(
                b"\x1b[38;2;0;0;0;48;2;255;255;255;58;2;1;2;3mX"
            )
            cell = terminal.snapshot().cell(0, 0)

            self.assertEqual(cell.foreground, (0, 0, 0))
            self.assertEqual(cell.background, (255, 255, 255))
            self.assertEqual(cell.underline_color, (1, 2, 3))

    def test_colon_truecolor_accepts_omitted_and_explicit_color_space(self):
        with Shitty(columns=4, rows=2) as terminal:
            terminal.write(
                b"\x1b[38:2:1:2:3mA"
                b"\x1b[38:2::4:5:6mB"
                b"\x1b[38:2:7:8:9:10mC"
            )
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.cell(0, 0).foreground, (1, 2, 3))
            self.assertEqual(snapshot.cell(1, 0).foreground, (4, 5, 6))
            self.assertEqual(snapshot.cell(2, 0).foreground, (8, 9, 10))

    def test_colon_indexed_colors_are_independent(self):
        with Shitty(columns=4, rows=2) as terminal:
            terminal.write(b"\x1b[38:5:196;48:5:21;58:5:46mX")
            cell = terminal.snapshot().cell(0, 0)

            self.assertEqual(cell.foreground, (255, 0, 0))
            self.assertEqual(cell.background, (0, 0, 255))
            self.assertEqual(cell.underline_color, (0, 255, 0))

    def test_default_underline_tracks_every_foreground_form(self):
        sequences = (
            (b"31", BASE_PALETTE[1]),
            (b"91", BASE_PALETTE[9]),
            (b"38;5;46", (0, 255, 0)),
            (b"38;2;1;2;3", (1, 2, 3)),
            (b"39", (255, 255, 255)),
        )
        with Shitty(columns=len(sequences), rows=2) as terminal:
            terminal.write(
                b"".join(b"\x1b[" + sequence + b"mX" for sequence, _ in sequences)
            )
            snapshot = terminal.snapshot()

            for column, (_, expected) in enumerate(sequences):
                with self.subTest(sequence=sequences[column][0]):
                    cell = snapshot.cell(column, 0)
                    self.assertEqual(cell.foreground, expected)
                    self.assertEqual(cell.underline_color, expected)

    def test_default_underline_tracks_bold_palette_changes(self):
        # Asserts bold-brightened palette indices; default off (issue 59).
        with Shitty(
            columns=4, rows=2, extra_arguments=("-boldColors",)
        ) as terminal:
            terminal.write(b"\x1b[31;4mA\x1b[1mB\x1b[22mC")
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.cell(0, 0).underline_color, BASE_PALETTE[1])
            self.assertEqual(snapshot.cell(1, 0).underline_color, BASE_PALETTE[9])
            self.assertEqual(snapshot.cell(2, 0).underline_color, BASE_PALETTE[1])

    def test_default_underline_tracks_displayed_foreground_under_inverse(self):
        with Shitty(columns=4, rows=2) as terminal:
            terminal.write(b"\x1b[31;44;4mA\x1b[7mB\x1b[27mC")
            snapshot = terminal.snapshot()

            for column in range(3):
                cell = snapshot.cell(column, 0)
                displayed_foreground = (
                    cell.background if cell.inverse else cell.foreground
                )
                self.assertEqual(cell.underline_color, displayed_foreground)

    def test_explicit_underline_color_survives_foreground_and_inverse(self):
        with Shitty(columns=4, rows=2) as terminal:
            terminal.write(
                b"\x1b[31;44;4;58;2;1;2;3mA"
                b"\x1b[32;7mB\x1b[27;59mC"
            )
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.cell(0, 0).underline_color, (1, 2, 3))
            self.assertEqual(snapshot.cell(1, 0).underline_color, (1, 2, 3))
            self.assertEqual(
                snapshot.cell(2, 0).underline_color,
                snapshot.cell(2, 0).foreground,
            )

    def test_all_defined_underline_styles_and_off(self):
        with Shitty(columns=6, rows=2) as terminal:
            terminal.write(
                b"".join(f"\x1b[4:{style}mX".encode() for style in range(6))
            )
            snapshot = terminal.snapshot()

            self.assertEqual(
                [snapshot.cell(column, 0).underline_style for column in range(6)],
                list(range(6)),
            )
            self.assertFalse(snapshot.cell(0, 0).underline)
            for column in range(1, 6):
                self.assertTrue(snapshot.cell(column, 0).underline)

    def test_unknown_underline_style_is_ignored(self):
        with Shitty(columns=4, rows=2) as terminal:
            terminal.write(b"\x1b[4:3mA\x1b[4:6mB\x1b[4:4294967295mC")
            snapshot = terminal.snapshot()

            self.assertEqual(
                [snapshot.cell(column, 0).underline_style for column in range(3)],
                [3, 3, 3],
            )

    def test_truncated_semicolon_truecolor_is_consumed_atomically(self):
        with Shitty(columns=4, rows=2) as terminal:
            terminal.write(b"\x1b[38;2;1;2mA\x1b[3mB")
            snapshot = terminal.snapshot()

            first = snapshot.cell(0, 0)
            self.assertEqual(first.foreground, (255, 255, 255))
            self.assertFalse(first.bold)
            self.assertFalse(first.faint)
            self.assertFalse(first.italic)
            self.assertTrue(snapshot.cell(1, 0).italic)

    def test_empty_colon_truecolor_component_defaults_to_zero(self):
        with Shitty(columns=4, rows=2) as terminal:
            terminal.write(b"\x1b[31m\x1b[38:2::1:2mA\x1b[32mB")
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.cell(0, 0).foreground, (0, 1, 2))
            self.assertEqual(snapshot.cell(1, 0).foreground, BASE_PALETTE[2])

    def test_invalid_extended_color_does_not_change_other_channels(self):
        with Shitty(columns=4, rows=2) as terminal:
            terminal.write(
                b"\x1b[38;2;1;2;3;48;2;4;5;6;58;2;7;8;9m"
                b"\x1b[38;5;256;48;2;4;999;6;58:5:256mX"
            )
            cell = terminal.snapshot().cell(0, 0)

            self.assertEqual(cell.foreground, (1, 2, 3))
            self.assertEqual(cell.background, (4, 5, 6))
            self.assertEqual(cell.underline_color, (7, 8, 9))

    def test_individual_resets_cover_every_attribute(self):
        with Shitty(columns=4, rows=2) as terminal:
            terminal.write(
                b"\x1b[1;2;3;4:5;5;7;8;9;53mA"
                b"\x1b[22;23;24;25;27;28;29;55mB"
            )
            first = terminal.snapshot().cell(0, 0)
            second = terminal.snapshot().cell(1, 0)

            self.assertTrue(first.bold)
            self.assertTrue(first.faint)
            self.assertTrue(first.italic)
            self.assertEqual(first.underline_style, 5)
            self.assertTrue(first.blink)
            self.assertTrue(first.conceal)
            self.assertTrue(first.strike)
            self.assertTrue(first.overline)
            self.assertFalse(second.bold)
            self.assertFalse(second.faint)
            self.assertFalse(second.italic)
            self.assertFalse(second.underline)
            self.assertFalse(second.blink)
            self.assertFalse(second.conceal)
            self.assertFalse(second.strike)
            self.assertFalse(second.overline)

    def test_empty_sgr_and_zero_reset_full_state(self):
        for reset in (b"\x1b[m", b"\x1b[0m"):
            with self.subTest(reset=reset):
                with Shitty(columns=4, rows=2) as terminal:
                    terminal.write(
                        b"\x1b[1;2;3;4:5;5;7;8;9;53;"
                        b"38;2;1;2;3;48;2;4;5;6;58;2;7;8;9mA"
                        + reset
                        + b"B"
                    )
                    cell = terminal.snapshot().cell(1, 0)

                    self.assertFalse(cell.bold)
                    self.assertFalse(cell.faint)
                    self.assertFalse(cell.italic)
                    self.assertFalse(cell.underline)
                    self.assertFalse(cell.blink)
                    self.assertFalse(cell.conceal)
                    self.assertFalse(cell.strike)
                    self.assertFalse(cell.overline)
                    self.assertEqual(cell.foreground, (255, 255, 255))
                    self.assertEqual(cell.background, (0, 0, 0))
                    self.assertEqual(cell.underline_color, cell.foreground)

    def test_unknown_sgr_is_ignored_and_parser_recovers(self):
        with Shitty(columns=4, rows=2) as terminal:
            terminal.write(b"\x1b[4294967295mA\x1b[1mB")
            snapshot = terminal.snapshot()

            self.assertFalse(snapshot.cell(0, 0).bold)
            self.assertTrue(snapshot.cell(1, 0).bold)


if __name__ == "__main__":
    unittest.main()
