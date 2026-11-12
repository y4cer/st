# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Public adaptations of all Alacritty index.rs and term/cell.rs units."""

import unittest

from harness import Shitty, put_rows


UPSTREAM_CASES = (
    "index::location_ordering",
    "index::sub",
    "index::sub_wrap",
    "index::sub_clamp",
    "index::sub_grid_clamp",
    "index::sub_none_clamp",
    "index::add",
    "index::add_wrap",
    "index::add_clamp",
    "index::add_grid_clamp",
    "index::add_none_clamp",
    "cell::cell_size_is_below_cap",
    "cell::line_length_works",
    "cell::line_length_works_with_wrapline",
)


def cursor(terminal):
    snapshot = terminal.snapshot()
    return snapshot.cursor_x, snapshot.cursor_y


def select(terminal, start, end):
    terminal.select_start(*start)
    terminal.select_update(*end)
    return terminal.select_finish()


class AlacrittyIndexCellTest(unittest.TestCase):
    def test_upstream_inventory_has_all_14_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 14)
        self.assertEqual(len(set(UPSTREAM_CASES)), 14)

    def test_location_ordering_is_row_major_in_both_selection_directions(self):
        with Shitty(columns=5, rows=3, save_lines=0) as terminal:
            terminal.write(put_rows(b"abcde", b"fghij", b"klmno"))
            forward = select(terminal, (1, 0), (3, 1))
            reverse = select(terminal, (3, 1), (1, 0))
            self.assertEqual(forward, b"bcde\nfgh")
            self.assertEqual(reverse, forward)

    def test_point_sub_moves_one_column(self):
        with Shitty(columns=42, rows=10) as terminal:
            terminal.write(b"\x1b[1;14H\x1b[1D")
            self.assertEqual(cursor(terminal), (12, 0))

    def test_point_sub_wraps_to_the_previous_row(self):
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write(b"\x1b[?45hABCDEZ\x1b[2;1H\x08")
            self.assertEqual(cursor(terminal), (4, 0))

    def test_point_sub_clamps_at_the_cursor_origin(self):
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write(b"\x1b[?45h\x1b[1;1H\x08\x1b[99D")
            self.assertEqual(cursor(terminal), (0, 0))

    def test_point_sub_grid_clamps_an_outside_selection_to_the_page(self):
        with Shitty(columns=5, rows=3, save_lines=0) as terminal:
            terminal.write(put_rows(b"abcde", b"fghij", b"klmno"))
            terminal.select_start(2, 1)
            terminal.select_update(-100, -100)
            state = terminal.selection_state()["snapped"]
            self.assertEqual(state[:2], (0, 0))

    def test_point_sub_without_a_boundary_traverses_the_complete_grid(self):
        with Shitty(columns=5, rows=2, save_lines=0) as terminal:
            terminal.write(put_rows(b"ABCDE", b"FGHIJ"))
            reverse = select(terminal, (5, 1), (0, 0))
            self.assertEqual(reverse, b"ABCDE\nFGHIJ")

    def test_point_add_moves_one_column(self):
        with Shitty(columns=42, rows=10) as terminal:
            terminal.write(b"\x1b[1;14H\x1b[1C")
            self.assertEqual(cursor(terminal), (14, 0))

    def test_point_add_wraps_to_the_next_row(self):
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write(b"ABCDEZ")
            self.assertEqual(terminal.snapshot().lines[:2], ["ABCDE", "Z    "])
            self.assertEqual(cursor(terminal), (1, 1))

    def test_point_add_clamps_at_the_cursor_page_end(self):
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write(b"\x1b[3;5H\x1b[99C")
            self.assertEqual(cursor(terminal), (4, 2))

    def test_point_add_grid_clamps_an_outside_selection_to_the_page(self):
        with Shitty(columns=5, rows=3, save_lines=0) as terminal:
            terminal.write(put_rows(b"abcde", b"fghij", b"klmno"))
            terminal.select_start(2, 1)
            terminal.select_update(100, 100)
            state = terminal.selection_state()["snapped"]
            self.assertEqual(state[2:], (5, 2))

    def test_point_add_without_a_boundary_traverses_from_first_to_last(self):
        with Shitty(columns=5, rows=2, save_lines=0) as terminal:
            terminal.write(put_rows(b"ABCDE", b"FGHIJ"))
            forward = select(terminal, (0, 0), (5, 1))
            self.assertEqual(forward, b"ABCDE\nFGHIJ")

    def test_cell_storage_retains_a_fully_attributed_public_cell(self):
        with Shitty(columns=4, rows=2, save_lines=0) as terminal:
            terminal.write(
                b"\x1b[1;3;4:3;5;7;9;53;"
                b"38;2;1;2;3;48;2;4;5;6;58;2;7;8;9mA"
            )
            cell = terminal.snapshot().cell(0, 0)
            self.assertEqual(cell.char, "A")
            self.assertTrue(cell.bold)
            self.assertTrue(cell.italic)
            self.assertTrue(cell.underline)
            self.assertEqual(cell.underline_style, 3)
            self.assertTrue(cell.blink)
            self.assertTrue(cell.inverse)
            self.assertTrue(cell.strike)
            self.assertTrue(cell.overline)
            self.assertEqual(cell.foreground, (1, 2, 3))
            self.assertEqual(cell.background, (4, 5, 6))
            self.assertEqual(cell.underline_color, (7, 8, 9))

    def test_line_length_stops_after_the_last_nonblank_cell(self):
        with Shitty(columns=10, rows=2, save_lines=0) as terminal:
            terminal.write(b"\x1b[1;6Ha")
            terminal.select_start(0, 0)
            terminal.select_extend(5, 0, cycle=True)
            self.assertEqual(terminal.select_finish(), b"     a")

    def test_wrapline_makes_the_entire_physical_row_part_of_the_line(self):
        with Shitty(columns=5, rows=2, save_lines=0) as terminal:
            terminal.write(put_rows(b"A", b"B"))
            terminal.set_wrapped(0)
            self.assertEqual(select(terminal, (0, 0), (1, 1)), b"A    B")


if __name__ == "__main__":
    unittest.main()
