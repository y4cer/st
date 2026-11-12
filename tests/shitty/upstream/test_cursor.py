# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


class CursorAndMovementTest(unittest.TestCase):
    def test_soft_reset_preserves_active_cursor_but_resets_saved_cursor(self):
        with Shitty(columns=8, rows=4) as terminal:
            terminal.write(b"\x1b[2;4H\x1b[!p\x1b[6n")
            self.assertEqual(terminal.read_input(), b"\x1b[2;4R")
            terminal.write(b"\x1b8\x1b[6n")
            self.assertEqual(terminal.read_input(), b"\x1b[1;1R")

    def test_carriage_return_backspace_and_tab(self):
        with Shitty(columns=10, rows=2) as terminal:
            terminal.write(b"abc\rX\tY\bZ")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0], "Xbc     Z ")
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (9, 0))

    def test_absolute_and_relative_cursor_movement(self):
        with Shitty(columns=8, rows=4) as terminal:
            terminal.write(b"\x1b[3;4HX\x1b[2A\x1b[2DY")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(3, 2).char, "X")
            self.assertEqual(snapshot.cell(2, 0).char, "Y")

    def test_ecma_position_backward_controls(self):
        with Shitty(columns=8, rows=4) as terminal:
            terminal.write(b"\x1b[4;7H\x1b[3j\x1b[2kX")
            self.assertEqual(terminal.snapshot().cell(3, 1).char, "X")

    def test_dec_save_and_restore_cursor(self):
        with Shitty(columns=8, rows=3) as terminal:
            terminal.write(b"\x1b[2;3H\x1b7\x1b[3;6HZ\x1b8X")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(2, 1).char, "X")
            self.assertEqual(snapshot.cell(5, 2).char, "Z")

    def test_sco_save_and_restore_cursor(self):
        with Shitty(columns=8, rows=3) as terminal:
            terminal.write(b"\x1b[2;3H\x1b[s\x1b[3;6HZ\x1b[uX")
            self.assertEqual(terminal.snapshot().cell(2, 1).char, "X")

    def test_sco_and_dec_controls_share_saved_cursor_state(self):
        with Shitty(columns=8, rows=3) as terminal:
            terminal.write(b"\x1b[2;3H\x1b[s\x1b[3;6H\x1b8A")
            terminal.write(b"\x1b[1;5H\x1b7\x1b[3;8H\x1b[uB")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(2, 1).char, "A")
            self.assertEqual(snapshot.cell(4, 0).char, "B")

    def test_sco_restores_attributes_protection_and_origin_mode(self):
        with Shitty(columns=8, rows=4) as terminal:
            terminal.write(
                b"\x1b[2;3H\x1b[1;31m\x1b[1\"q\x1b[s"
                b"\x1b[0m\x1b[0\"q"
                b"\x1b[2;3r\x1b[?69h\x1b[2;7s\x1b[?6h"
                b"\x1b[uX\x1b[1;1HY"
            )
            snapshot = terminal.snapshot()
            restored = snapshot.cell(2, 1)
            self.assertEqual(restored.char, "X")
            self.assertTrue(restored.bold)
            self.assertTrue(restored.protected)
            self.assertEqual(snapshot.cell(0, 0).char, "Y")

    def test_sco_saved_cursor_is_independent_between_screen_buffers(self):
        with Shitty(columns=8, rows=4) as terminal:
            terminal.write(
                b"\x1b[2;2H\x1b[s"
                b"\x1b[?47h\x1b[3;4H\x1b[s"
                b"\x1b[?47l\x1b[uM"
                b"\x1b[?47h\x1b[uA"
            )
            self.assertEqual(terminal.snapshot().cell(3, 2).char, "A")
            terminal.write(b"\x1b[?47l")
            self.assertEqual(terminal.snapshot().cell(1, 1).char, "M")

    def test_cleared_alternate_screen_preserves_its_saved_cursor(self):
        with Shitty(columns=8, rows=4) as terminal:
            terminal.write(
                b"\x1b[?1049h\x1b[3;4H\x1b7"
                b"\x1b[?1049l"
                b"\x1b[1;1H\x1b[?1049h\x1b8A"
            )
            self.assertEqual(terminal.snapshot().cell(3, 2).char, "A")

    def test_sco_restore_after_soft_reset_uses_home_defaults(self):
        with Shitty(columns=8, rows=4) as terminal:
            terminal.write(b"\x1b[3;4H\x1b[!p\x1b[4;7H\x1b[uX")
            self.assertEqual(terminal.snapshot().cell(0, 0).char, "X")

    def test_saved_cursor_can_be_restored_repeatedly(self):
        sequences = (b"\x1b7", b"\x1b[s")
        restores = (b"\x1b8", b"\x1b[u")
        for save, restore in zip(sequences, restores):
            with self.subTest(save=save):
                with Shitty(columns=8, rows=3) as terminal:
                    terminal.write(
                        b"\x1b[2;3H" + save +
                        b"\x1b[3;6H" + restore + b"A" +
                        b"\x1b[1;1H" + restore + b"B"
                    )
                    snapshot = terminal.snapshot()
                    self.assertEqual(snapshot.cell(2, 1).char, "B")
                    self.assertEqual(snapshot.cell(5, 2).char, " ")

    def test_scrolling_region_scrolls_without_moving_outer_rows(self):
        with Shitty(columns=5, rows=4) as terminal:
            terminal.write(
                b"AAAAA\r\nBBBBB\r\nCCCCC\r\nDDDDD"
                b"\x1b[2;3r\x1b[3;1H\n"
            )
            self.assertEqual(
                terminal.snapshot().lines,
                ["AAAAA", "CCCCC", "     ", "DDDDD"],
            )

    def test_batched_autowrap_inside_horizontal_margins(self):
        with Shitty(columns=8, rows=6) as terminal:
            terminal.write(
                b"00000000\r\n11111111\r\n22222222\r\n33333333\r\nijklmnop"
                b"\x1b[2;5r\x1b[?69h\x1b[3;6s"
                b"\x1b[5;3HWXYZaaaabbbbccccddddeeeeffff"
            )
            snapshot = terminal.snapshot()
            self.assertEqual(
                snapshot.lines,
                [
                    "00000000",
                    "11cccc11",
                    "22dddd22",
                    "33eeee33",
                    "ijffffop",
                    "        ",
                ],
            )
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (5, 4))

    def test_index_controls_do_not_scroll_outside_horizontal_margins(self):
        for control in (b"\n", b"\v", b"\f", b"\x1bD", b"\x1bE"):
            with self.subTest(control=control):
                with Shitty(columns=8, rows=6) as terminal:
                    terminal.write(
                        b"\x1b[2;5r\x1b[?69h\x1b[2;5s"
                        b"\x1b[5;3HX"
                        b"\x1b[5;6H" + control
                    )
                    snapshot = terminal.snapshot()
                    self.assertEqual(snapshot.cell(2, 4).char, "X")
                    self.assertEqual(snapshot.cursor_y, 4)

    def test_reverse_index_does_not_scroll_outside_horizontal_margins(self):
        with Shitty(columns=8, rows=6) as terminal:
            terminal.write(
                b"\x1b[2;5r\x1b[?69h\x1b[2;5s"
                b"\x1b[2;3HX"
                b"\x1b[2;6H\x1bM"
            )
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(2, 1).char, "X")
            self.assertEqual(snapshot.cursor_y, 1)

    def test_column_index_moves_normally_outside_horizontal_margins(self):
        with Shitty(columns=10, rows=4) as terminal:
            terminal.write(b"\x1b[?69h\x1b[3;7s")

            terminal.write(b"\x1b[1;2H\x1b6")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 0))

            terminal.write(b"\x1b[1;8H\x1b9")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (8, 0))

            terminal.write(b"\x1b[1;1H\x1b6\x1b[1;10H\x1b9")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (9, 0))

    def test_column_index_scrolls_at_page_edges(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"x\x1b[1;1H\x1b6")
            self.assertEqual(terminal.snapshot().lines[0], " x   ")

        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"\x1b[1;5Hx\x1b9")
            self.assertEqual(terminal.snapshot().lines[0], "   x ")

    def test_column_index_scrolls_at_margin_outside_vertical_region(self):
        cases = (
            (b"\x1b[1;3H\x1b6", "AB CDEGH"),
            (b"\x1b[1;6H\x1b9", "ABDEF GH"),
        )
        for control, expected in cases:
            with self.subTest(control=control):
                with Shitty(columns=8, rows=4) as terminal:
                    terminal.write(
                        b"\x1b[2;1HABCDEFGH"
                        b"\x1b[2;4r\x1b[?69h\x1b[3;6s" + control
                    )
                    self.assertEqual(terminal.snapshot().lines[1], expected)

    def test_sco_save_and_restore_cursor(self):
        # The ANSI.SYS pair: CSI s saves, CSI u restores - the same slot
        # DECSC uses, reachable while DECSLRM has not claimed CSI s.
        with Shitty(columns=8, rows=3) as terminal:
            terminal.write(b"AB\x1b[sCD\x1b[2;1HX\x1b[uZ")
            self.assertEqual(terminal.snapshot().lines[0], "ABZD    ")


if __name__ == "__main__":
    unittest.main()
