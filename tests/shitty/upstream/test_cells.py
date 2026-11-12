# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


class CellStateTest(unittest.TestCase):
    def test_control_reports_current_pen_without_writing_a_cell(self):
        with Shitty(columns=4, rows=2) as terminal:
            terminal.write(b"\x1b[1;2;3;4:3;5;7;8;9;38:5:42;48;2;1;2;3m")
            pen = terminal.pen_state()
            self.assertTrue(pen.bold)
            self.assertTrue(pen.faint)
            self.assertTrue(pen.italic)
            self.assertTrue(pen.underline)
            self.assertEqual(pen.underline_style, 3)
            self.assertTrue(pen.blink)
            self.assertTrue(pen.conceal)
            self.assertTrue(pen.strike)
            self.assertTrue(pen.inverse)
            self.assertEqual(pen.foreground_index, 42)
            self.assertEqual(pen.background, (1, 2, 3))

    def test_model_digest_covers_rich_state_but_not_refresh_count(self):
        payload = b"\x1b[38;2;1;2;3;48;5;4mA\xcc\x81"
        with (
            Shitty(columns=4, rows=2) as whole,
            Shitty(columns=4, rows=2) as chunked,
        ):
            whole.write(payload)
            chunked.write_chunks(payload[:21], payload[21:])

            self.assertNotEqual(
                whole.snapshot().refresh_count,
                chunked.snapshot().refresh_count,
            )
            self.assertEqual(whole.model_digest(), chunked.model_digest())
            self.assertEqual(
                whole.model_snapshot().cells,
                chunked.model_snapshot().cells,
            )

            chunked.write(b"\x1b[1;1H\x1b[38;2;2;2;3mB")
            self.assertNotEqual(whole.model_digest(), chunked.model_digest())

    def test_model_snapshot_exposes_color_sources_and_graphemes(self):
        with Shitty(columns=4, rows=2) as terminal:
            terminal.write(
                b"\x1b[38;5;1;48;2;4;5;6mA\xcc\x81"
                b"\x1b[58;5;46m\xe7\x95\x8c"
            )
            snapshot = terminal.model_snapshot()

            first = snapshot.cell(0, 0)
            self.assertEqual(first.foreground_index, 1)
            self.assertEqual(first.background_index, -1)
            self.assertEqual(first.grapheme, (ord("A"), 0x301))

            wide = snapshot.cell(1, 0)
            self.assertTrue(wide.double_width)
            self.assertEqual(wide.underline_index, 46)
            self.assertEqual(wide.grapheme, ())
            self.assertTrue(snapshot.cell(2, 0).double_width_continuation)

    def test_sgr_attributes_and_truecolor_are_observable(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[1;3;4;7;38;2;1;2;3;48;2;4;5;6mX")
            cell = terminal.snapshot().cell(0, 0)

            self.assertEqual(cell.char, "X")
            self.assertTrue(cell.bold)
            self.assertTrue(cell.italic)
            self.assertTrue(cell.underline)
            # ECMA-48 SGR 7 is a rendition attribute. Keep the logical colors
            # observable and let the renderer apply the negative image.
            self.assertTrue(cell.inverse)
            self.assertEqual(cell.foreground, (1, 2, 3))
            self.assertEqual(cell.background, (4, 5, 6))

    def test_sgr_resets_individual_attributes(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[1;3;4;7mA\x1b[22;23;24;27mB")
            snapshot = terminal.snapshot()

            first = snapshot.cell(0, 0)
            second = snapshot.cell(1, 0)
            self.assertTrue(first.bold and first.italic)
            self.assertTrue(first.underline)
            self.assertFalse(second.bold or second.italic)
            self.assertFalse(second.underline)

    def test_wide_character_occupies_two_cells(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write("界".encode())
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.cell(0, 0).char, "界")
            self.assertTrue(snapshot.cell(0, 0).double_width)
            self.assertTrue(snapshot.cell(1, 0).double_width_continuation)

    def test_wide_character_wraps_before_last_column(self):
        with Shitty(columns=4, rows=2) as terminal:
            terminal.write(b"abc" + "界".encode())
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.lines, ["abc ", "界   "])
            self.assertTrue(snapshot.cell(2, 0).wrapped)
            self.assertFalse(snapshot.cell(3, 0).wrapped)
            self.assertTrue(snapshot.cell(0, 1).double_width)
            self.assertTrue(snapshot.cell(1, 1).double_width_continuation)

    def test_overwriting_wide_cell_half_clears_the_other_half(self):
        for column in (1, 2):
            with self.subTest(column=column):
                with Shitty(columns=6, rows=2) as terminal:
                    terminal.write("A界B".encode())
                    terminal.write(f"\x1b[1;{column + 1}H".encode() + b"X")
                    snapshot = terminal.snapshot()

                    self.assertFalse(snapshot.cell(1, 0).double_width)
                    self.assertFalse(
                        snapshot.cell(2, 0).double_width_continuation
                    )
                    self.assertEqual(snapshot.cell(column, 0).char, "X")

    def test_autowrap_is_recorded_on_last_cell(self):
        with Shitty(columns=4, rows=2) as terminal:
            terminal.write(b"abcde")
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.lines, ["abcd", "e   "])
            self.assertTrue(snapshot.cell(3, 0).wrapped)

    def test_ansi_bright_and_256_color_palette(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[91;104mA\x1b[38;5;196;48;5;21mB")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(0, 0).foreground, (255, 85, 85))
            self.assertEqual(snapshot.cell(0, 0).background, (85, 85, 255))
            self.assertEqual(snapshot.cell(1, 0).foreground, (255, 0, 0))
            self.assertEqual(snapshot.cell(1, 0).background, (0, 0, 255))

    def test_default_colors_can_be_restored(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[31;42mA\x1b[39;49mB")
            snapshot = terminal.snapshot()
            self.assertNotEqual(
                snapshot.cell(0, 0).foreground,
                snapshot.cell(1, 0).foreground,
            )
            self.assertEqual(snapshot.cell(1, 0).foreground, (255, 255, 255))
            self.assertEqual(snapshot.cell(1, 0).background, (0, 0, 0))

    def test_out_of_range_extended_colors_are_ignored(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(
                b"\x1b[31;42m"
                b"\x1b[38;5;256;48;5;4294967295mX"
            )
            cell = terminal.snapshot().cell(0, 0)

            self.assertEqual(cell.foreground, (170, 0, 0))
            self.assertEqual(cell.background, (0, 170, 0))

    def test_out_of_range_truecolor_components_are_ignored(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(
                b"\x1b[31;42m"
                b"\x1b[38;2;256;2;3;48;2;4;5;999mX"
            )
            cell = terminal.snapshot().cell(0, 0)

            self.assertEqual(cell.foreground, (170, 0, 0))
            self.assertEqual(cell.background, (0, 170, 0))

    def test_extended_sgr_attributes_and_resets(self):
        with Shitty(columns=12, rows=2) as terminal:
            terminal.write(b"\x1b[1;2;5;8;9;53mA\x1b[22;25;28;29;55mB")
            first = terminal.snapshot().cell(0, 0)
            second = terminal.snapshot().cell(1, 0)

            self.assertTrue(first.bold)
            self.assertTrue(first.faint)
            self.assertTrue(first.blink)
            self.assertTrue(first.conceal)
            self.assertTrue(first.strike)
            self.assertTrue(first.overline)
            self.assertFalse(second.bold)
            self.assertFalse(second.faint)
            self.assertFalse(second.blink)
            self.assertFalse(second.conceal)
            self.assertFalse(second.strike)
            self.assertFalse(second.overline)

    def test_colon_sgr_colors_and_underline_styles(self):
        with Shitty(columns=12, rows=2) as terminal:
            terminal.write(
                b"\x1b[4:3;38:2::1:2:3;48:5:21;58:2::4:5:6mA"
                b"\x1b[4:0;59mB"
            )
            first = terminal.snapshot().cell(0, 0)
            second = terminal.snapshot().cell(1, 0)

            self.assertEqual(first.underline_style, 3)
            self.assertEqual(first.foreground, (1, 2, 3))
            self.assertEqual(first.background, (0, 0, 255))
            self.assertEqual(first.underline_color, (4, 5, 6))
            self.assertEqual(second.underline_style, 0)
            self.assertEqual(second.underline_color, second.foreground)

    def test_alternative_font_sgr_does_not_change_weight_or_slant(self):
        with Shitty(columns=12, rows=2) as terminal:
            terminal.write(b"\x1b[1;3mA\x1b[10mB\x1b[19mC")
            snapshot = terminal.snapshot()

            for column in range(3):
                self.assertTrue(snapshot.cell(column, 0).bold)
                self.assertTrue(snapshot.cell(column, 0).italic)


if __name__ == "__main__":
    unittest.main()
