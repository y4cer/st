# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


class GhosttyStyleAndDecalnTest(unittest.TestCase):
    def test_default_style_is_empty(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"A")
            cell = terminal.model_snapshot().cell(0, 0)
            self.assertEqual(cell.char, "A")
            self.assertFalse(
                cell.bold
                or cell.faint
                or cell.italic
                or cell.underline
                or cell.blink
                or cell.inverse
                or cell.conceal
                or cell.strike
                or cell.overline
            )

    def test_bold_style_is_attached_to_cell(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"\x1b[1mA")
            cell = terminal.model_snapshot().cell(0, 0)
            self.assertEqual(cell.char, "A")
            self.assertTrue(cell.bold)

    def test_overwriting_styled_cell_releases_observable_style(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"\x1b[1mA\x1b[1;1H\x1b[0mB")
            cell = terminal.model_snapshot().cell(0, 0)
            self.assertEqual(cell.char, "B")
            self.assertFalse(cell.bold)

    def test_overwriting_one_cell_keeps_style_on_neighbor(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"\x1b[1mAB\x1b[1;1H\x1b[0mC")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[0], "CB   ")
            self.assertFalse(snapshot.cell(0, 0).bold)
            self.assertTrue(snapshot.cell(1, 0).bold)

    def test_normal_cell_on_styled_row_does_not_inherit_style(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"\x1b[1mA\x1b[0mB")
            snapshot = terminal.model_snapshot()
            self.assertTrue(snapshot.cell(0, 0).bold)
            self.assertFalse(snapshot.cell(1, 0).bold)

    def test_decaln_fills_screen_homes_cursor_and_damages_every_row(self):
        with Shitty(columns=3, rows=3) as terminal:
            terminal.write(b"A\r\nB\x1b#8")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines, ["EEE", "EEE", "EEE"])
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 0))
            self.assertEqual(terminal.last_update(), (9, 3))
            self.assertEqual(terminal.last_update_rows(), (0, 1, 2))

    def test_decaln_resets_both_margin_pairs(self):
        with Shitty(columns=3, rows=3) as terminal:
            terminal.write(
                b"\x1b[?69h\x1b[2;3s\x1b[2;3r\x1b[?6h"
                b"\x1b#8\x1b[T"
            )
            self.assertEqual(terminal.model_snapshot().lines, ["   ", "EEE", "EEE"])

            terminal.write(b"\x1b[3;3H\x1b[99B\x1b[99C")
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (2, 2))

    def test_decaln_uses_default_cell_rendition(self):
        with Shitty(columns=3, rows=2) as terminal:
            terminal.write(
                b"\x1b[1;3;4:3;7;38;2;12;34;56;48;2;78;90;12m"
                b"\x1b#8"
            )
            for cell in terminal.model_snapshot().cells:
                self.assertEqual(cell.char, "E")
                self.assertEqual(cell.foreground, (255, 255, 255))
                self.assertEqual(cell.background, (0, 0, 0))
                self.assertFalse(
                    cell.bold
                    or cell.italic
                    or cell.underline
                    or cell.inverse
                )

    def test_decaln_replaces_protected_graphemes_with_unprotected_ascii(self):
        with Shitty(columns=3, rows=3) as terminal:
            terminal.write(
                b"\x1b[1\"q"
                + "👨‍👩‍👧".encode()
                + b"\x1b#8"
            )
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines, ["EEE", "EEE", "EEE"])
            for cell in snapshot.cells:
                self.assertFalse(cell.protected)
                self.assertEqual(cell.grapheme, ())

            # DECALN ignores protection while filling, but does not end the
            # protected-area state selected by DECSCA.
            terminal.write(b"X")
            self.assertTrue(terminal.model_snapshot().cell(0, 0).protected)


if __name__ == "__main__":
    unittest.main()
