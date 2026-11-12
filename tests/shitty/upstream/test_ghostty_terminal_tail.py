# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


def assert_wide_cells_are_paired(test, snapshot):
    for row in range(snapshot.rows):
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


class GhosttyTerminalTailTest(unittest.TestCase):
    def assert_private_mode(self, terminal, mode, state):
        terminal.write(f"\x1b[?{mode}$p".encode())
        self.assertEqual(
            terminal.read_input(),
            f"\x1b[?{mode};{state}$y".encode(),
        )

    def test_full_reset_clears_non_default_pen_and_semantic_state(self):
        with Shitty(columns=8, rows=3) as terminal:
            default_pen = terminal.pen_state()
            terminal.write(
                b"\x1b[1;3;4;38;2;255;0;127;48;2;127;0;255m"
                b"\x1b]133;B\x1b\\"
            )
            self.assertNotEqual(terminal.pen_state(), default_pen)

            terminal.write(b"\x1bcX")

            self.assertEqual(terminal.pen_state(), default_pen)
            cell = terminal.model_snapshot().cell(0, 0)
            self.assertEqual(cell.char, "X")
            self.assertEqual(cell.semantic, 0)
            self.assertFalse(cell.bold or cell.italic or cell.underline)

    def test_full_reset_closes_active_hyperlink(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(
                b"\x1b]8;;https://example.com\x1b\\A"
                b"\x1bcB"
            )
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.cell(0, 0).char, "B")
            self.assertEqual(snapshot.cell(0, 0).hyperlink, 0)

    def test_full_reset_discards_saved_cursor_and_rendition(self):
        with Shitty(columns=8, rows=4) as terminal:
            terminal.write(
                b"\x1b[3;4H"
                b"\x1b[38;2;255;0;127;48;2;127;0;255m"
                b"\x1b7"
                b"\x1bc"
                b"\x1b8X"
            )
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 0))
            self.assertEqual(snapshot.cell(0, 0).char, "X")
            self.assertEqual(snapshot.cell(0, 0).foreground, (255, 255, 255))
            self.assertEqual(snapshot.cell(0, 0).background, (0, 0, 0))

    def test_full_reset_homes_cursor_and_resets_origin_mode(self):
        with Shitty(columns=8, rows=5) as terminal:
            terminal.write(
                b"\x1b[2;4r\x1b[?69h\x1b[2;7s"
                b"\x1b[?6h\x1b[3;4H"
                b"\x1bc"
            )
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 0))
            self.assert_private_mode(terminal, 6, 2)

    def test_full_reset_clears_alternate_kitty_keyboard_state(self):
        with Shitty(columns=8, rows=3) as terminal:
            terminal.write(
                b"\x1b[?1049h"
                b"\x1b[>31u"
                b"\x1b[?1049l"
                b"\x1bc"
                b"\x1b[?1049h"
            )
            self.assertEqual(terminal.state()[3], 0)

    def test_full_reset_restores_default_grapheme_mode(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[?2027l")
            self.assert_private_mode(terminal, 2027, 2)
            terminal.write(b"\x1bc")
            self.assert_private_mode(terminal, 2027, 1)

    def test_resize_after_wide_right_edge_then_print_is_valid(self):
        with Shitty(columns=3, rows=3) as terminal:
            terminal.write("x😀".encode())
            terminal.resize(2, 3)
            terminal.write(b"\x1b[1;2H" + "😀".encode())
            assert_wide_cells_are_paired(self, terminal.model_snapshot())

    def test_resize_with_active_horizontal_margins_and_large_rep(self):
        with Shitty(columns=70, rows=23) as terminal:
            terminal.write(
                b"\x1b[?69h"
                b"0"
                b"\x1b[?40h"
            )
            terminal.resize(70, 23)
            terminal.write(b"\x1b[2;0s\x1b[1850b")
            terminal.resize(70, 23)
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.columns, snapshot.rows), (70, 23))
            assert_wide_cells_are_paired(self, snapshot)

    def test_resize_without_wrap_still_reflows_primary_content(self):
        with Shitty(columns=4, rows=2) as terminal:
            terminal.write(b"\x1b[?7l0123")
            terminal.resize(2, 2)
            self.assertEqual(terminal.snapshot().lines, ["01", "23"])

    def test_resize_with_wrap_reflows_pending_line(self):
        with Shitty(columns=4, rows=2) as terminal:
            terminal.write(b"0123")
            terminal.resize(2, 2)
            self.assertEqual(terminal.snapshot().lines, ["01", "23"])

    def test_resize_preserves_many_unique_positioned_styles(self):
        with Shitty(columns=30, rows=30) as terminal:
            stream = bytearray()
            for row in range(30):
                for column in range(30):
                    stream.extend(
                        f"\x1b[{row + 1};{column + 1}H"
                        f"\x1b[48;2;{column};{row};0mX".encode()
                    )
            terminal.write(bytes(stream))
            terminal.resize(60, 30)

            snapshot = terminal.model_snapshot()
            for row in range(30):
                for column in range(30):
                    cell = snapshot.cell(column, row)
                    self.assertEqual(cell.char, "X")
                    self.assertEqual(cell.background, (column, row, 0))

    def test_resize_reflows_many_unique_stream_styles(self):
        with Shitty(columns=30, rows=30) as terminal:
            stream = bytearray()
            for index in range(30 * 30):
                stream.extend(
                    f"\x1b[48;2;{index >> 8};{index & 255};0mX".encode()
                )
            terminal.write(bytes(stream))
            terminal.resize(60, 30)

            snapshot = terminal.model_snapshot()
            for index in range(30 * 30):
                cell = snapshot.cell(index % 60, index // 60)
                self.assertEqual(cell.char, "X")
                self.assertEqual(
                    cell.background,
                    (index >> 8, index & 255, 0),
                )

    def test_saved_cursor_tracks_cell_across_reflow(self):
        with Shitty(columns=2, rows=3) as terminal:
            terminal.write(b"1A2B\x1b[2;2H\x1b7")
            terminal.resize(5, 3)
            terminal.write(b"\x1b8")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0], "1A2B ")
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (3, 0))
            self.assertEqual(snapshot.cell(3, 0).char, "B")

    def test_saved_pending_wrap_is_normalized_across_reflow(self):
        with Shitty(columns=2, rows=3) as terminal:
            terminal.write(b"1A2B\x1b7")
            terminal.resize(5, 3)
            terminal.write(b"\x1b8")
            self.assertFalse(terminal.cursor_pending_wrap())
            terminal.write(b"X")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0], "1A2BX")
            self.assertTrue(terminal.cursor_pending_wrap())

    def test_deccolm_is_ignored_without_allow_mode(self):
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(b"\x1b[?3h")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.columns, snapshot.rows), (5, 5))
            self.assert_private_mode(terminal, 3, 2)

    def test_deccolm_reset_selects_eighty_columns_when_allowed(self):
        with Shitty(columns=80, rows=5) as terminal:
            terminal.write(b"\x1b[?40h\x1b[?3h\x1b[?3l")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.columns, snapshot.rows), (80, 5))

    def test_deccolm_resets_pending_wrap(self):
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(b"ABCDE")
            self.assertTrue(terminal.cursor_pending_wrap())
            terminal.write(b"\x1b[?40h\x1b[?3l")
            self.assertFalse(terminal.cursor_pending_wrap())

    def test_deccolm_clear_uses_current_background(self):
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(
                b"\x1b[48;2;255;0;0m"
                b"\x1b[?40h\x1b[?3l"
            )
            self.assertEqual(
                terminal.model_snapshot().cell(0, 0).background,
                (255, 0, 0),
            )

    def test_deccolm_resets_both_margin_pairs(self):
        with Shitty(columns=80, rows=5) as terminal:
            terminal.write(
                b"\x1b[?69h"
                b"\x1b[2;3r"
                b"\x1b[3;80s"
                b"\x1b[?40h\x1b[?3h\x1b[?3l"
                b"\x1b[?6h\x1b[HX"
            )
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(0, 0).char, "X")
            self.assert_private_mode(terminal, 69, 1)

    def test_mode_47_retains_alternate_contents(self):
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(
                b"1A"
                b"\x1b[?47h2B"
                b"\x1b[?47l"
            )
            self.assertEqual(terminal.snapshot().lines[0], "1A   ")
            terminal.write(b"\x1b[?47h")
            self.assertEqual(terminal.snapshot().lines[0], "  2B ")

    def test_mode_47_copies_rendition_both_directions(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(
                b"\x1b[38;2;255;0;127m"
                b"\x1b[?47h"
                b"\x1b[38;2;0;255;0m"
                b"\x1b[?47lX"
            )
            self.assertEqual(
                terminal.model_snapshot().cell(0, 0).foreground,
                (0, 255, 0),
            )

    def test_mode_1047_clears_alternate_contents_on_exit(self):
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(
                b"1A"
                b"\x1b[?1047h2B"
                b"\x1b[?1047l"
            )
            self.assertEqual(terminal.snapshot().lines[0], "1A   ")
            terminal.write(b"\x1b[?1047h")
            self.assertEqual(terminal.snapshot().lines, ["     "] * 5)

    def test_mode_1047_copies_rendition_both_directions(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(
                b"\x1b[38;2;255;0;127m"
                b"\x1b[?1047h"
                b"\x1b[38;2;0;255;0m"
                b"\x1b[?1047lX"
            )
            self.assertEqual(
                terminal.model_snapshot().cell(0, 0).foreground,
                (0, 255, 0),
            )

    def test_mode_1049_clears_alt_and_restores_primary_cursor(self):
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(
                b"1A"
                b"\x1b[?1049h2B"
                b"\x1b[?1049lC"
            )
            self.assertEqual(terminal.snapshot().lines[0], "1AC  ")
            terminal.write(b"\x1b[?1049h")
            self.assertEqual(terminal.snapshot().lines, ["     "] * 5)

    def test_full_region_delete_lines_repairs_wide_margin_boundary(self):
        with Shitty(columns=80, rows=24) as terminal:
            terminal.write(
                b"\x1b[10;39H"
                + "中".encode()
                + b"\x1b[?69h"
                b"\x1b[5;39s"
                b"\x1b[24S"
            )
            snapshot = terminal.model_snapshot()
            assert_wide_cells_are_paired(self, snapshot)
            self.assertEqual(snapshot.cell(38, 9).char, " ")
            self.assertEqual(snapshot.cell(39, 9).char, " ")


if __name__ == "__main__":
    unittest.main()
