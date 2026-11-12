# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Public adaptations of all Alacritty terminal selection.rs tests."""

import unittest

from harness import Shitty, put_rows


UPSTREAM_CASES = (
    "single_cell_left_to_right",
    "single_cell_right_to_left",
    "between_adjacent_cells_left_to_right",
    "between_adjacent_cells_right_to_left",
    "across_adjacent_lines_upward_final_cell_exclusive",
    "selection_bigger_then_smaller",
    "line_selection",
    "semantic_selection",
    "simple_selection",
    "block_selection",
    "simple_is_empty",
    "block_is_empty",
    "rotate_in_region_up",
    "rotate_in_region_down",
    "rotate_in_region_up_block",
    "range_intersection",
)


BORDER = 2
GLYPH = 10
ROWS = tuple(bytes((ord("A") + row,)) * 5 for row in range(10))


def x(column, fraction):
    return BORDER + (column + fraction) * GLYPH


def y(row):
    return BORDER + (row + 0.5) * GLYPH


def drag(terminal, start, end, *, rectangular=False, intermediate=()):
    terminal.button(0, True, x=x(*start[:2]), y=y(start[2]), time=1)
    if rectangular:
        terminal.select_rectangular()
    for column, fraction, row in intermediate:
        terminal.pointer(x(column, fraction), y(row))
    terminal.pointer(x(*end[:2]), y(end[2]))
    return terminal.button(
        0,
        False,
        x=x(*end[:2]),
        y=y(end[2]),
        time=1.01,
    )


def selection_terminal():
    return Shitty(
        columns=5,
        rows=10,
        save_lines=0,
        glyph_px=GLYPH,
        glyph_py=GLYPH,
    )


def select_mode(terminal, start, end, mode):
    terminal.select_start(*start)
    if mode == "block":
        terminal.select_rectangular()
    terminal.select_update(*end)
    if mode == "word":
        terminal.select_extend(*end, cycle=True)
    elif mode == "line":
        terminal.select_extend(*end, cycle=True)
        terminal.select_extend(*end, cycle=True)


class AlacrittySelectionTest(unittest.TestCase):
    def test_upstream_inventory_has_all_16_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 16)
        self.assertEqual(len(set(UPSTREAM_CASES)), 16)

    @unittest.expectedFailure
    def test_single_cell_left_to_right_uses_covered_halves(self):
        with selection_terminal() as terminal:
            terminal.write(put_rows(*ROWS))
            self.assertEqual(drag(terminal, (0, 0.1, 0), (0, 0.9, 0)), b"A")

    @unittest.expectedFailure
    def test_single_cell_right_to_left_uses_covered_halves(self):
        with selection_terminal() as terminal:
            terminal.write(put_rows(*ROWS))
            self.assertEqual(drag(terminal, (0, 0.9, 0), (0, 0.1, 0)), b"A")

    @unittest.expectedFailure
    def test_gap_between_adjacent_cells_is_empty_left_to_right(self):
        with selection_terminal() as terminal:
            terminal.write(put_rows(*ROWS))
            self.assertEqual(drag(terminal, (0, 0.9, 0), (1, 0.1, 0)), b"")
            self.assertFalse(terminal.has_selection())

    @unittest.expectedFailure
    def test_gap_between_adjacent_cells_is_empty_right_to_left(self):
        with selection_terminal() as terminal:
            terminal.write(put_rows(*ROWS))
            self.assertEqual(drag(terminal, (1, 0.1, 0), (0, 0.9, 0)), b"")
            self.assertFalse(terminal.has_selection())

    @unittest.expectedFailure
    def test_multiline_end_on_right_half_includes_the_final_cell(self):
        with selection_terminal() as terminal:
            terminal.write(put_rows(*ROWS))
            self.assertEqual(
                drag(terminal, (1, 0.9, 0), (1, 0.9, 1)),
                b"CDE\nFG",
            )

    @unittest.expectedFailure
    def test_reversing_and_shrinking_selection_recomputes_cell_sides(self):
        with selection_terminal() as terminal:
            terminal.write(put_rows(*ROWS))
            self.assertEqual(
                drag(
                    terminal,
                    (1, 0.9, 1),
                    (0, 0.9, 0),
                    intermediate=((1, 0.9, 0),),
                ),
                b"BCDE\nFG",
            )

    def test_line_selection_rotates_with_full_screen_scroll(self):
        with selection_terminal() as terminal:
            terminal.write(put_rows(*ROWS))
            select_mode(terminal, (1, 9), (1, 4), "line")
            self.assertEqual(terminal.selection_state()["snapped"], (0, 4, 5, 9))
            terminal.write(b"\x1b[4S")
            self.assertEqual(terminal.selection_state()["snapped"], (0, 0, 5, 5))

    def test_semantic_selection_rotates_with_full_screen_scroll(self):
        rows = list(ROWS)
        rows[4] = b" EEEE"
        rows[9] = b"JJJJ "
        with selection_terminal() as terminal:
            terminal.write(put_rows(*rows))
            select_mode(terminal, (3, 9), (1, 4), "word")
            before = terminal.select_finish()
            self.assertEqual(before, b"EEEE\nFFFFF\nGGGGG\nHHHHH\nIIIII\nJJJJ")
            terminal.write(b"\x1b[4S")
            self.assertEqual(terminal.select_finish(), before)

    def test_simple_selection_rotates_with_full_screen_scroll(self):
        with selection_terminal() as terminal:
            terminal.write(put_rows(*ROWS))
            select_mode(terminal, (3, 9), (1, 4), "simple")
            before = terminal.select_finish()
            terminal.write(b"\x1b[4S")
            self.assertEqual(terminal.select_finish(), before)
            self.assertEqual(terminal.selection_state()["snapped"][1::2], (0, 5))

    def test_block_selection_rotates_with_full_screen_scroll(self):
        with selection_terminal() as terminal:
            terminal.write(put_rows(*ROWS))
            select_mode(terminal, (3, 9), (1, 4), "block")
            before = terminal.select_finish()
            terminal.write(b"\x1b[4S")
            self.assertEqual(terminal.select_finish(), before)
            state = terminal.selection_state()
            self.assertTrue(state["snapped_rectangular"])
            self.assertEqual(state["snapped"][1::2], (0, 5))

    @unittest.expectedFailure
    def test_simple_selection_between_cell_halves_is_empty(self):
        with selection_terminal() as terminal:
            terminal.write(put_rows(*ROWS))
            self.assertEqual(drag(terminal, (0, 0.9, 1), (1, 0.1, 1)), b"")
            self.assertFalse(terminal.has_selection())

    @unittest.expectedFailure
    def test_block_empty_state_depends_on_columns_and_cell_sides(self):
        with selection_terminal() as terminal:
            terminal.write(put_rows(*ROWS))
            self.assertEqual(
                drag(
                    terminal,
                    (0, 0.9, 1),
                    (1, 0.1, 0),
                    rectangular=True,
                ),
                b"",
            )
            self.assertFalse(terminal.has_selection())

    @unittest.expectedFailure
    def test_linear_selection_is_clipped_at_top_of_scrolled_region(self):
        with selection_terminal() as terminal:
            terminal.write(put_rows(*ROWS))
            select_mode(terminal, (2, 4), (3, 7), "simple")
            terminal.write(b"\x1b[2;9r\x1b[4S")
            self.assertEqual(terminal.selection_state()["snapped"], (0, 1, 4, 3))

    @unittest.expectedFailure
    def test_linear_selection_is_clipped_at_bottom_of_scrolled_region(self):
        with selection_terminal() as terminal:
            terminal.write(put_rows(*ROWS))
            select_mode(terminal, (1, 1), (3, 4), "simple")
            terminal.write(b"\x1b[2;9r\x1b[5T")
            self.assertEqual(terminal.selection_state()["snapped"], (1, 6, 5, 8))

    @unittest.expectedFailure
    def test_block_selection_clips_rows_without_expanding_columns(self):
        with selection_terminal() as terminal:
            terminal.write(put_rows(*ROWS))
            select_mode(terminal, (2, 4), (3, 7), "block")
            terminal.write(b"\x1b[2;9r\x1b[4S")
            state = terminal.selection_state()
            self.assertTrue(state["snapped_rectangular"])
            self.assertEqual(state["snapped"], (2, 1, 4, 3))

    def test_writes_only_clear_a_selection_when_rows_intersect(self):
        with selection_terminal() as terminal:
            terminal.write(put_rows(*ROWS))
            select_mode(terminal, (1, 3), (3, 6), "simple")
            before = terminal.selection_state()
            terminal.write(b"\x1b[2;1HX")
            self.assertEqual(terminal.selection_state(), before)
            terminal.write(b"\x1b[5;1HY")
            self.assertFalse(terminal.has_selection())


if __name__ == "__main__":
    unittest.main()
