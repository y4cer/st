# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


class ChangeRectangleAttributesTest(unittest.TestCase):
    def test_kitty_full_sgr_transaction(self):
        with Shitty(columns=5, rows=5, save_lines=0) as terminal:
            terminal.write(b"\x1b[$r")
            terminal.write(
                b"\x1b[;;;;4:3;38:5:10;48:2:1:2:3;1$r"
            )

            snapshot = terminal.model_snapshot()
            for cell in snapshot.cells:
                self.assertTrue(cell.bold)
                self.assertFalse(cell.italic)
                self.assertEqual(cell.underline_style, 3)
                self.assertEqual(cell.foreground_index, 10)
                self.assertEqual(cell.background, (1, 2, 3))

            terminal.write(b"\x1b[1;2;2;3;22;39$r")
            snapshot = terminal.model_snapshot()
            for row in range(snapshot.rows):
                for column in range(snapshot.columns):
                    cell = snapshot.cell(column, row)
                    in_stream_extent = (
                        row == 0 and column >= 1
                    ) or (
                        row == 1 and column <= 2
                    )
                    self.assertEqual(cell.bold, not in_stream_extent)
                    self.assertEqual(
                        cell.foreground_index,
                        -2 if in_stream_extent else 10,
                    )

            terminal.write(
                b"\x1b[2*x"
                b"\x1b[3;2;4;3;34$r"
                b"\x1b[*x"
            )
            snapshot = terminal.model_snapshot()
            for row in range(snapshot.rows):
                for column in range(snapshot.columns):
                    changed = 2 <= row <= 3 and 1 <= column <= 2
                    expected = 4 if changed else (
                        -2 if (
                            row == 0 and column >= 1
                        ) or (
                            row == 1 and column <= 2
                        ) else 10
                    )
                    self.assertEqual(
                        snapshot.cell(column, row).foreground_index,
                        expected,
                    )


    def test_every_attribute_and_default_color_can_be_changed(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(b"abc\r\ndef\x1b[1;1;2;3;3;9;53;5;8$r")
            cell = terminal.snapshot().cell(0, 0)
            self.assertEqual(
                (cell.italic, cell.strike, cell.overline, cell.blink, cell.conceal),
                (True, True, True, True, True),
            )
            terminal.write(b"\x1b[1;1;2;3;44;34;58;5;1$r")
            cell = terminal.snapshot().cell(0, 0)
            self.assertEqual((cell.background, cell.foreground), ((0, 0, 170), (0, 0, 170)))
            terminal.write(b"\x1b[1;1;2;3;49;39;59$r")
            cell = terminal.snapshot().cell(0, 0)
            self.assertEqual(
                (cell.background, cell.foreground, cell.underline_color),
                ((0, 0, 0), (255, 255, 255), (255, 255, 255)),
            )


    def test_underline_color_reaches_cells_carrying_a_grapheme(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write("éx".encode() + b"\x1b[1;1;1;2;58;5;1$r")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(0, 0).underline_color, (170, 0, 0))
            self.assertEqual(snapshot.cell(1, 0).underline_color, (170, 0, 0))


if __name__ == "__main__":
    unittest.main()
