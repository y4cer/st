# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty, put_rows


UPSTREAM_CASES = (
    "PageList resize reflow less cols wrap preserves semantic prompt",
    "PageList resize reflow less cols no wrapped rows",
    "PageList resize reflow less cols wrapped rows",
    "PageList resize reflow less cols wrapped rows with graphemes",
    "PageList resize reflow less cols cursor in wrapped row",
    "PageList resize reflow less cols wraps spacer head",
    "PageList resize reflow less cols cursor goes to scrollback",
    "PageList resize reflow less cols cursor in unchanged row",
    "PageList resize reflow less cols cursor in blank cell",
    "PageList resize reflow less cols cursor in final blank cell",
    "PageList resize reflow less cols cursor in wrapped blank cell",
    "PageList resize reflow less cols blank lines",
    "PageList resize reflow less cols blank lines between",
    "PageList resize reflow less cols blank lines between no scrollback",
    "PageList resize reflow less cols cursor not on last line preserves location",
    "PageList resize reflow less cols copy style",
    "PageList resize reflow less cols to eliminate a wide char",
    "PageList resize reflow less cols to wrap a wide char",
    "PageList resize reflow less cols to wrap a multi-codepoint grapheme with a spacer head",
    "PageList resize reflow less cols copy kitty placeholder",
)


PROMPT = 1
KITTY_PLACEHOLDER = "\U0010eeee"


def visible_lines(terminal):
    return tuple(line.rstrip() for line in terminal.snapshot().lines)


def osc133(action):
    return b"\x1b]133;" + action + b"\x1b\\"


class GhosttyPageListReflowShrinkTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 20)
        self.assertEqual(len(set(UPSTREAM_CASES)), 20)

    def test_prompt_marker_on_first_line_is_copied_to_its_soft_continuation(self):
        with Shitty(columns=4, rows=4, save_lines=0) as terminal:
            terminal.write(osc133(b"P") + b"ABCD")

            terminal.resize(2, 4)
            snapshot = terminal.snapshot()

            self.assertEqual(visible_lines(terminal)[:2], ("AB", "CD"))
            self.assertEqual(tuple(snapshot.cell(column, 0).semantic for column in range(2)), (PROMPT, PROMPT))
            self.assertEqual(tuple(snapshot.cell(column, 1).semantic for column in range(2)), (PROMPT, PROMPT))

    def test_short_hard_rows_do_not_reflow_when_they_fit_the_new_width(self):
        with Shitty(columns=10, rows=3, save_lines=0) as terminal:
            terminal.write(put_rows(b"0123", b"4567", b"89ab"))

            terminal.resize(5, 3)

            self.assertEqual(visible_lines(terminal), ("0123", "4567", "89ab"))

    def test_full_hard_rows_split_without_becoming_one_logical_line(self):
        with Shitty(columns=4, rows=2, save_lines=4) as terminal:
            terminal.write(put_rows(b"0123", b"4567"))

            terminal.resize(2, 2)

            self.assertEqual(terminal.all_text(), ("01", "23", "45", "67"))
            self.assertEqual(visible_lines(terminal), ("45", "67"))
            terminal.wheel_up(10)
            self.assertEqual(visible_lines(terminal), ("01", "23"))

    def test_graphemes_follow_their_cells_when_hard_rows_split(self):
        first = "01a\N{COMBINING ACUTE ACCENT}3"
        second = "45b\N{COMBINING ACUTE ACCENT}7"
        with Shitty(columns=4, rows=2, save_lines=4) as terminal:
            terminal.write(put_rows(first.encode(), second.encode()))

            terminal.resize(2, 2)
            bottom = terminal.model_snapshot()

            self.assertEqual(bottom.cell(0, 1).grapheme, tuple(map(ord, "b\N{COMBINING ACUTE ACCENT}")))
            terminal.wheel_up(10)
            top = terminal.model_snapshot()
            self.assertEqual(top.cell(0, 1).grapheme, tuple(map(ord, "a\N{COMBINING ACUTE ACCENT}")))

    def test_cursor_in_second_hard_row_tracks_its_new_continuation(self):
        with Shitty(columns=4, rows=2, save_lines=4) as terminal:
            terminal.write(put_rows(b"0123", b"4567") + b"\x1b[2;3H")

            terminal.resize(2, 2)
            snapshot = terminal.snapshot()

            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 1))
            self.assertEqual(snapshot.cell(0, 1).char, "6")

    def test_width_shrink_drops_the_old_spacer_before_wrapping_the_wide_glyph(self):
        with Shitty(columns=4, rows=3, save_lines=0) as terminal:
            terminal.write("xxx😀".encode())

            terminal.resize(3, 3)
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.lines[0], "xxx")
            self.assertTrue(snapshot.cell(0, 1).double_width)
            self.assertTrue(snapshot.cell(1, 1).double_width_continuation)

    def test_anchor_in_first_reflowed_hard_row_moves_into_scrollback(self):
        with Shitty(columns=4, rows=2, save_lines=4) as terminal:
            terminal.write(put_rows(b"0123", b"4567"))
            terminal.select_start(2, 0)
            terminal.select_update(3, 0)

            terminal.resize(2, 2)

            self.assertEqual(terminal.select_finish(), b"2")
            terminal.wheel_up(10)
            self.assertEqual(visible_lines(terminal), ("01", "23"))

    def test_cursor_in_short_row_keeps_its_column_after_width_shrink(self):
        with Shitty(columns=4, rows=2, save_lines=0) as terminal:
            terminal.write(put_rows(b"01", b"23") + b"\x1b[1;2H")

            terminal.resize(2, 2)

            self.assertEqual((terminal.snapshot().cursor_x, terminal.snapshot().cursor_y), (1, 0))

    def test_cursor_in_an_interior_blank_cell_survives_width_shrink(self):
        with Shitty(columns=6, rows=2, save_lines=0) as terminal:
            terminal.write(put_rows(b"01", b"23") + b"\x1b[1;3H")

            terminal.resize(4, 2)

            self.assertEqual((terminal.snapshot().cursor_x, terminal.snapshot().cursor_y), (2, 0))

    def test_cursor_in_the_final_new_blank_cell_survives_width_shrink(self):
        with Shitty(columns=6, rows=2, save_lines=0) as terminal:
            terminal.write(put_rows(b"01", b"23") + b"\x1b[1;4H")

            terminal.resize(4, 2)

            self.assertEqual((terminal.snapshot().cursor_x, terminal.snapshot().cursor_y), (3, 0))

    def test_cursor_past_content_clamps_to_the_last_content_column(self):
        with Shitty(columns=6, rows=2, save_lines=0) as terminal:
            terminal.write(put_rows(b"01", b"23") + b"\x1b[1;6H")

            terminal.resize(4, 2)

            self.assertEqual((terminal.snapshot().cursor_x, terminal.snapshot().cursor_y), (1, 0))

    def test_trailing_blank_rows_make_room_for_a_split_content_row(self):
        with Shitty(columns=4, rows=3, save_lines=0) as terminal:
            terminal.write(b"0123")

            terminal.resize(2, 3)

            self.assertEqual(visible_lines(terminal), ("01", "23", ""))

    def test_blank_hard_row_between_content_lines_survives_reflow_with_history(self):
        with Shitty(columns=4, rows=3, save_lines=4) as terminal:
            terminal.write(put_rows(b"0123", b"", b"4567"))

            terminal.resize(2, 3)

            self.assertEqual(visible_lines(terminal), ("", "45", "67"))
            terminal.wheel_up(10)
            self.assertEqual(visible_lines(terminal), ("01", "23", ""))

    def test_short_content_around_a_blank_line_needs_no_scrollback(self):
        with Shitty(columns=5, rows=3, save_lines=0) as terminal:
            terminal.write(put_rows(b"A", b"", b"C"))

            terminal.resize(2, 3)

            self.assertEqual(visible_lines(terminal), ("A", "", "C"))

    def test_nonfinal_cursor_and_selection_keep_their_short_hard_rows(self):
        with Shitty(columns=5, rows=5, save_lines=1) as terminal:
            terminal.write(put_rows(b"01", b"23", b"45", b"67", b"89"))
            terminal.select_start(0, 0)
            terminal.select_update(2, 0)
            terminal.write(b"\x1b[2;2H")

            terminal.resize(4, 5)

            self.assertEqual((terminal.snapshot().cursor_x, terminal.snapshot().cursor_y), (1, 1))
            self.assertEqual(terminal.select_finish(), b"01")

    def test_bold_style_is_copied_to_every_new_soft_row(self):
        with Shitty(columns=4, rows=2, save_lines=0) as terminal:
            terminal.write(b"\x1b[1mABC\x1b[0m")

            terminal.resize(2, 2)
            snapshot = terminal.snapshot()

            self.assertTrue(snapshot.cell(0, 0).bold)
            self.assertTrue(snapshot.cell(1, 0).bold)
            self.assertTrue(snapshot.cell(0, 1).bold)

    def test_one_column_grid_eliminates_an_unrepresentable_wide_glyph(self):
        with Shitty(columns=2, rows=1, save_lines=0) as terminal:
            terminal.write("😀".encode())

            terminal.resize(1, 1)
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.lines, [" "])
            self.assertFalse(snapshot.cell(0, 0).double_width)
            self.assertFalse(snapshot.cell(0, 0).double_width_continuation)

    def test_width_shrink_wraps_a_wide_glyph_as_an_intact_cell(self):
        with Shitty(columns=3, rows=1, save_lines=1) as terminal:
            terminal.write("x😀".encode())

            terminal.resize(2, 1)
            bottom = terminal.snapshot()

            self.assertTrue(bottom.cell(0, 0).double_width)
            self.assertTrue(bottom.cell(1, 0).double_width_continuation)
            terminal.wheel_up(1)
            top = terminal.snapshot()
            self.assertEqual(top.lines[0][0], "x")
            self.assertFalse(top.cell(1, 0).double_width)
            self.assertFalse(top.cell(1, 0).double_width_continuation)

    def test_family_graphemes_remain_intact_around_the_new_wide_spacer(self):
        family = "👨\N{ZERO WIDTH JOINER}👨\N{ZERO WIDTH JOINER}👦\N{ZERO WIDTH JOINER}👦"
        with Shitty(columns=4, rows=2, save_lines=0) as terminal:
            terminal.write((family * 2).encode())

            terminal.resize(3, 2)
            snapshot = terminal.model_snapshot()

            expected = tuple(map(ord, family))
            self.assertEqual(snapshot.cell(0, 0).grapheme, expected)
            self.assertEqual(snapshot.cell(0, 1).grapheme, expected)
            self.assertTrue(snapshot.cell(0, 0).double_width)
            self.assertTrue(snapshot.cell(0, 1).double_width)

    def test_kitty_unicode_placeholder_stream_survives_row_split(self):
        with Shitty(columns=4, rows=2, save_lines=0) as terminal:
            terminal.write((KITTY_PLACEHOLDER * 3).encode())

            terminal.resize(2, 2)
            snapshot = terminal.model_snapshot()
            placeholders = [cell.char for cell in snapshot.cells if cell.char == KITTY_PLACEHOLDER]

            self.assertEqual(placeholders, [KITTY_PLACEHOLDER] * 3)


if __name__ == "__main__":
    unittest.main()
