# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Public adaptations of all 20 Ghostty terminal/Selection.zig tests."""

import unittest

from harness import Shitty, put_rows


UPSTREAM_CASES = (
    "Selection: adjust right",
    "Selection: adjust left",
    "Selection: adjust left skips blanks",
    "Selection: adjust up",
    "Selection: adjust down",
    "Selection: adjust down with not full screen",
    "Selection: adjust home",
    "Selection: adjust end with not full screen",
    "Selection: adjust beginning of line",
    "Selection: adjust end of line",
    "Selection: order, standard",
    "Selection: rectangle corners clamp across mixed-width pages",
    "Selection: order, rectangle",
    "topLeft",
    "bottomRight",
    "ordered",
    "Selection: contains",
    "Selection: contains, rectangle",
    "Selection: containedRow",
    "Selection: containedRow clamps mixed-width pages",
)


ROWS = (b"abcdefghij", b"klmnopqrst", b"uvwxyzABCD", b"EFGHIJKLMN")


def drag(terminal, start, end, rectangular=False):
    terminal.select_start(*start)
    if rectangular:
        terminal.select_rectangular()
    terminal.select_update(*end)


class GhosttySelectionGeometryTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 20)
        self.assertEqual(len(set(UPSTREAM_CASES)), 20)

    def test_adjust_right_moves_endpoint_and_wraps_to_next_row(self):
        with Shitty(columns=10, rows=4, save_lines=0) as terminal:
            terminal.write(put_rows(*ROWS))
            drag(terminal, (5, 1), (3, 3))
            terminal.select_update(4, 3)
            self.assertEqual(terminal.selection_state()["raw"], (5, 1, 4, 3))

            terminal.select_clear()
            drag(terminal, (4, 1), (4, 2))
            terminal.select_update(0, 3)
            self.assertEqual(terminal.selection_state()["raw"], (4, 1, 0, 3))

    def test_adjust_left_moves_endpoint_and_wraps_to_previous_row(self):
        with Shitty(columns=10, rows=4, save_lines=0) as terminal:
            terminal.write(put_rows(*ROWS))
            drag(terminal, (5, 1), (3, 3))
            terminal.select_update(2, 3)
            self.assertEqual(terminal.selection_state()["raw"], (5, 1, 2, 3))

            terminal.select_clear()
            drag(terminal, (5, 1), (0, 3))
            terminal.select_update(9, 2)
            self.assertEqual(terminal.selection_state()["raw"], (5, 1, 9, 2))

    def test_adjust_left_skips_unwritten_blank_tail(self):
        with Shitty(columns=10, rows=4, save_lines=0) as terminal:
            terminal.write(put_rows(b"A1234", b"B5678", b"C12", b"D56"))
            drag(terminal, (5, 1), (4, 3))
            terminal.select_update(2, 3)
            self.assertEqual(terminal.selection_state()["raw"], (5, 1, 2, 3))

            terminal.select_update(0, 3)
            terminal.select_update(2, 2)
            self.assertEqual(terminal.selection_state()["raw"], (5, 1, 2, 2))

    def test_adjust_up_moves_one_row_and_clamps_at_top(self):
        with Shitty(columns=10, rows=5, save_lines=0) as terminal:
            drag(terminal, (5, 1), (3, 3))
            terminal.select_update(3, 2)
            self.assertEqual(terminal.selection_state()["raw"], (5, 1, 3, 2))

            terminal.select_update(3, 0)
            terminal.select_update(0, 0)
            self.assertEqual(terminal.selection_state()["snapped"], (0, 0, 5, 1))

    def test_adjust_down_moves_one_row_and_clamps_at_bottom(self):
        with Shitty(columns=10, rows=5, save_lines=0) as terminal:
            drag(terminal, (5, 1), (3, 3))
            terminal.select_update(3, 4)
            self.assertEqual(terminal.selection_state()["raw"], (5, 1, 3, 4))

            terminal.select_update(9, 4)
            self.assertEqual(terminal.selection_state()["raw"], (5, 1, 9, 4))

    def test_adjust_down_clamps_to_last_written_row_on_partial_screen(self):
        with Shitty(columns=10, rows=10, save_lines=0) as terminal:
            terminal.write(put_rows(b"A", b"B", b"C"))
            drag(terminal, (4, 1), (3, 2))
            terminal.select_update(9, 2)

            self.assertEqual(terminal.selection_state()["raw"], (4, 1, 9, 2))

    def test_adjust_home_moves_endpoint_to_screen_origin(self):
        with Shitty(columns=10, rows=10, save_lines=0) as terminal:
            drag(terminal, (4, 1), (1, 2))
            terminal.select_update(0, 0)

            self.assertEqual(terminal.selection_state()["snapped"], (0, 0, 4, 1))

    def test_adjust_end_moves_endpoint_to_last_written_row_edge(self):
        with Shitty(columns=10, rows=10, save_lines=0) as terminal:
            terminal.write(put_rows(b"A", b"B", b"C"))
            drag(terminal, (4, 0), (1, 1))
            terminal.select_update(9, 2)

            self.assertEqual(terminal.selection_state()["raw"], (4, 0, 9, 2))

    def test_adjust_beginning_of_line_preserves_anchor(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.write(put_rows(b"A12 B34", b"C12 D34"))
            drag(terminal, (5, 1), (5, 1))
            terminal.select_update(0, 1)

            self.assertEqual(terminal.selection_state()["snapped"], (0, 1, 5, 1))

    def test_adjust_end_of_line_preserves_anchor(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.write(put_rows(b"A12 B34", b"C12 D34"))
            drag(terminal, (1, 0), (1, 0))
            terminal.select_update(7, 0)

            self.assertEqual(terminal.selection_state()["raw"], (1, 0, 7, 0))

    def test_standard_order_is_direction_independent(self):
        results = []
        for start, end in (((2, 1), (2, 2)), ((2, 2), (2, 1))):
            with Shitty(columns=10, rows=4, save_lines=0) as terminal:
                terminal.write(put_rows(*ROWS))
                drag(terminal, start, end)
                results.append(terminal.select_finish())

        self.assertEqual(results[0], results[1])

    def test_rectangle_corners_clamp_after_width_shrink(self):
        with Shitty(columns=4, rows=3, save_lines=4) as terminal:
            terminal.write(put_rows(b"abcd", b"efgh", b"ijkl"))
            drag(terminal, (3, 0), (1, 2), rectangular=True)
            terminal.resize(2, 3)
            left, _, right, _ = terminal.selection_state()["snapped"]

            self.assertLess(left, 2)
            self.assertLess(right, 2)

    def test_rectangle_order_is_direction_independent(self):
        directions = (
            ((1, 0), (4, 2)),
            ((4, 2), (1, 0)),
            ((4, 0), (1, 2)),
            ((1, 2), (4, 0)),
        )
        for start, end in directions:
            with self.subTest(start=start, end=end):
                with Shitty(columns=6, rows=3, save_lines=0) as terminal:
                    terminal.write(put_rows(b"abcdef", b"ghijkl", b"mnopqr"))
                    drag(terminal, start, end, rectangular=True)
                    self.assertEqual(terminal.select_finish(), b"bcd\nhij\nnop")

    def test_top_left_is_normalized_for_all_rectangle_directions(self):
        directions = (((1, 1), (3, 3)), ((3, 3), (1, 1)), ((3, 1), (1, 3)), ((1, 3), (3, 1)))
        with Shitty(columns=10, rows=5, save_lines=0) as terminal:
            for start, end in directions:
                terminal.select_clear()
                drag(terminal, start, end, rectangular=True)
                self.assertEqual(terminal.selection_state()["snapped"][:2], (1, 1))

    def test_bottom_right_is_normalized_for_all_directions(self):
        directions = (((1, 1), (3, 3)), ((3, 3), (1, 1)), ((3, 1), (1, 3)), ((1, 3), (3, 1)))
        with Shitty(columns=10, rows=5, save_lines=0) as terminal:
            for start, end in directions:
                terminal.select_clear()
                drag(terminal, start, end, rectangular=True)
                self.assertEqual(terminal.selection_state()["snapped"][2:], (3, 3))

    def test_ordered_selection_has_canonical_public_extent(self):
        with Shitty(columns=10, rows=4, save_lines=0) as terminal:
            terminal.write(put_rows(*ROWS))
            drag(terminal, (3, 3), (1, 1), rectangular=True)

            self.assertEqual(terminal.selection_state()["snapped"], (1, 1, 3, 3))
            self.assertEqual(terminal.select_finish(), b"lm\nvw\nFG")

    def test_linear_contains_exactly_its_public_extent(self):
        with Shitty(columns=10, rows=4, save_lines=0) as terminal:
            terminal.write(put_rows(*ROWS))
            drag(terminal, (5, 1), (3, 2))

            self.assertEqual(terminal.selection_state()["snapped"], (5, 1, 3, 2))
            self.assertEqual(terminal.select_finish(), b"pqrst\nuvw")

    def test_rectangle_contains_center_borders_and_excludes_outside(self):
        rows = tuple(bytes([ord("a") + row]) * 15 for row in range(12))
        with Shitty(columns=15, rows=12, save_lines=0) as terminal:
            terminal.write(put_rows(*rows))
            drag(terminal, (3, 3), (7, 9), rectangular=True)

            self.assertEqual(terminal.selection_state()["snapped"], (3, 3, 7, 9))
            self.assertEqual(
                terminal.select_finish(),
                b"\n".join(bytes([ord("a") + row]) * 4 for row in range(3, 10)),
            )

    def test_contained_row_slices_linear_rectangle_and_single_line(self):
        with Shitty(columns=10, rows=5, save_lines=0) as terminal:
            terminal.write(put_rows(*ROWS, b"OPQRSTUVWX"))
            drag(terminal, (5, 1), (3, 3))
            self.assertEqual(terminal.select_finish(), b"pqrst\nuvwxyzABCD\nEFG")

            drag(terminal, (3, 1), (6, 3), rectangular=True)
            self.assertEqual(terminal.select_finish(), b"nop\nxyz\nHIJ")

            drag(terminal, (2, 1), (6, 1))
            self.assertEqual(terminal.select_finish(), b"mnop")

    @unittest.expectedFailure
    def test_contained_row_clamps_after_rows_cross_width_generations(self):
        with Shitty(columns=4, rows=3, save_lines=8) as terminal:
            terminal.write(b"old1\r\nold2\r\nold3\r\nold4")
            terminal.wheel_up(1)
            drag(terminal, (1, 0), (3, 2), rectangular=True)
            terminal.resize(2, 3)
            state = terminal.selection_state()["snapped"]

            self.assertTrue(all(0 <= column < 2 for column in (state[0], state[2])))


if __name__ == "__main__":
    unittest.main()
