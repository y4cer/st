# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Public adaptations of all Alacritty grid and storage unit tests."""

import unittest

from harness import Shitty, put_rows


UPSTREAM_CASES = (
    "storage.with_capacity",
    "storage.indexing",
    "storage.indexing_above_inner_len",
    "storage.rotate",
    "storage.grow_after_zero",
    "storage.grow_before_zero",
    "storage.shrink_before_zero",
    "storage.shrink_after_zero",
    "storage.shrink_before_and_after_zero",
    "storage.truncate_invisible_lines",
    "storage.truncate_invisible_lines_beginning",
    "storage.shrink_then_grow",
    "storage.initialize",
    "storage.rotate_wrap_zero",
    "grid.scroll_up",
    "grid.scroll_down",
    "grid.scroll_down_with_history",
    "grid.test_iter",
    "grid.shrink_reflow",
    "grid.shrink_reflow_twice",
    "grid.shrink_reflow_empty_cell_inside_line",
    "grid.grow_reflow",
    "grid.grow_reflow_multiline",
    "grid.grow_reflow_disabled",
    "grid.shrink_reflow_disabled",
    "grid.accurate_size_hint",
)


def visible_lines(terminal):
    return tuple(line.rstrip() for line in terminal.snapshot().lines)


def numbered_lines(first, last):
    return b"\r\n".join(str(value).encode() for value in range(first, last + 1))


class AlacrittyGridStorageTest(unittest.TestCase):
    def test_upstream_inventory_has_all_26_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 26)
        self.assertEqual(len(set(UPSTREAM_CASES)), 26)

    def test_storage_capacity_publishes_exact_blank_page_geometry(self):
        with Shitty(columns=4, rows=3, save_lines=1) as terminal:
            snapshot = terminal.model_snapshot()

            self.assertEqual((snapshot.columns, snapshot.rows), (4, 3))
            self.assertEqual(len(snapshot.cells), 12)
            self.assertEqual(visible_lines(terminal), ("", "", ""))
            self.assertEqual(terminal.scrollback_state(), (0, 3, 3, 0))

    def test_rotated_storage_indexes_history_and_page_in_logical_order(self):
        with Shitty(columns=3, rows=3, save_lines=3) as terminal:
            terminal.write(numbered_lines(0, 4))

            self.assertEqual(terminal.all_text(), ("0", "1", "2", "3", "4"))
            self.assertEqual(visible_lines(terminal), ("2", "3", "4"))
            terminal.wheel_up(2)
            self.assertEqual(visible_lines(terminal), ("0", "1", "2"))

    def test_public_indexing_clamps_history_and_rejects_page_overrun(self):
        with Shitty(columns=2, rows=2, save_lines=1) as terminal:
            terminal.write(numbered_lines(0, 3))
            terminal.wheel_up(1_000)
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.view_offset, 1)
            self.assertEqual(snapshot.view_offset, terminal.scrollback_state()[0])
            self.assertEqual(visible_lines(terminal), ("1", "2"))
            with self.assertRaises(IndexError):
                snapshot.cell(-1, 0)
            with self.assertRaises(IndexError):
                snapshot.cell(0, snapshot.rows)

    def test_rotation_followed_by_shrink_keeps_the_newest_logical_tail(self):
        with Shitty(columns=3, rows=3, save_lines=3) as terminal:
            terminal.write(numbered_lines(0, 8))
            terminal.resize(3, 2)

            self.assertEqual(terminal.all_text(), ("4", "5", "6", "7", "8"))
            self.assertEqual(visible_lines(terminal), ("7", "8"))
            self.assertEqual(terminal.scrollback_state()[0], 3)

    def test_growing_unrotated_page_appends_blank_visible_capacity(self):
        with Shitty(columns=3, rows=3, save_lines=0) as terminal:
            terminal.write(put_rows(b"A", b"B"))
            terminal.resize(3, 4)
            snapshot = terminal.snapshot()

            self.assertEqual(visible_lines(terminal), ("A", "B", "", ""))
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 1))

    def test_growing_rotated_page_pulls_history_before_adding_blanks(self):
        with Shitty(columns=3, rows=3, save_lines=3) as terminal:
            terminal.write(numbered_lines(0, 3))
            terminal.resize(3, 5)

            self.assertEqual(terminal.scrollback_state()[0], 0)
            self.assertEqual(visible_lines(terminal), ("0", "1", "2", "3", ""))

    def test_shrinking_at_bottom_moves_evicted_prefix_into_history(self):
        with Shitty(columns=3, rows=4, save_lines=4) as terminal:
            terminal.write(put_rows(b"A", b"B", b"C", b"D"))
            terminal.resize(3, 2)

            self.assertEqual(terminal.scrollback_state()[0], 2)
            self.assertEqual(visible_lines(terminal), ("C", "D"))
            self.assertEqual(terminal.all_text(), ("A", "B", "C", "D"))

    def test_shrinking_unused_tail_keeps_top_content_without_history(self):
        with Shitty(columns=3, rows=4, save_lines=4) as terminal:
            terminal.write(put_rows(b"A", b"B"))
            terminal.write(b"\x1b[H")
            terminal.resize(3, 2)

            self.assertEqual(terminal.scrollback_state()[0], 0)
            self.assertEqual(visible_lines(terminal), ("A", "B"))

    def test_region_rotation_reuses_rows_between_untouched_edges(self):
        with Shitty(columns=3, rows=6, save_lines=0) as terminal:
            terminal.write(put_rows(b"A", b"B", b"C", b"D", b"E", b"F"))
            terminal.write(b"\x1b[2;5r\x1b[2;1H\x1b[2S\x1b[r")

            self.assertEqual(visible_lines(terminal), ("A", "D", "E", "", "", "F"))

    def test_truncating_spare_storage_keeps_only_the_visible_grid(self):
        with Shitty(columns=4, rows=3, save_lines=8) as terminal:
            terminal.write(numbered_lines(0, 8))
            terminal.resize(4, 2)
            terminal.resize(4, 3)
            before = visible_lines(terminal)
            terminal.write(b"\x1b[3J")

            self.assertEqual(terminal.scrollback_state()[0], 0)
            self.assertEqual(visible_lines(terminal), before)
            self.assertEqual(terminal.all_text(), before)

    def test_truncating_rotated_prefix_snaps_view_to_surviving_page(self):
        with Shitty(columns=4, rows=3, save_lines=6) as terminal:
            terminal.write(numbered_lines(0, 7))
            terminal.wheel_up(3)
            terminal.write(b"\x1b[3J")

            self.assertEqual(terminal.snapshot().view_offset, 0)
            self.assertEqual(terminal.scrollback_state()[0], 0)
            self.assertEqual(visible_lines(terminal), ("5", "6", "7"))

    def test_shrink_then_grow_reuses_history_in_logical_order(self):
        with Shitty(columns=3, rows=6, save_lines=6) as terminal:
            terminal.write(put_rows(b"A", b"B", b"C", b"D", b"E", b"F"))
            terminal.resize(3, 3)
            self.assertEqual(visible_lines(terminal), ("D", "E", "F"))
            terminal.resize(3, 4)

            self.assertEqual(visible_lines(terminal), ("C", "D", "E", "F"))
            self.assertEqual(terminal.scrollback_state()[0], 2)

    def test_later_growth_initializes_rows_after_history_capacity_was_full(self):
        with Shitty(columns=3, rows=2, save_lines=5) as terminal:
            terminal.write(numbered_lines(0, 9))
            self.assertEqual(terminal.scrollback_state()[0], 5)
            terminal.resize(3, 5)

            self.assertEqual(terminal.scrollback_state()[0], 2)
            self.assertEqual(visible_lines(terminal), ("5", "6", "7", "8", "9"))

    def test_many_rotations_wrap_storage_without_changing_logical_order(self):
        with Shitty(columns=3, rows=3, save_lines=2) as terminal:
            terminal.write(numbered_lines(0, 50))

            self.assertEqual(terminal.all_text(), ("46", "47", "48", "49", "50"))
            terminal.wheel_up(10_000)
            self.assertEqual(visible_lines(terminal), ("46", "47", "48"))
            terminal.wheel_down(10_000)
            self.assertEqual(visible_lines(terminal), ("48", "49", "50"))

    def test_scroll_up_moves_rows_up_and_clears_the_vacated_suffix(self):
        rows = tuple(str(value).encode() for value in range(10))
        with Shitty(columns=2, rows=10, save_lines=0) as terminal:
            terminal.write(put_rows(*rows))
            terminal.write(b"\x1b[2S")

            self.assertEqual(
                visible_lines(terminal),
                ("2", "3", "4", "5", "6", "7", "8", "9", "", ""),
            )

    def test_scroll_down_moves_rows_down_and_clears_the_vacated_prefix(self):
        rows = tuple(str(value).encode() for value in range(10))
        with Shitty(columns=2, rows=10, save_lines=0) as terminal:
            terminal.write(put_rows(*rows))
            terminal.write(b"\x1b[2T")

            self.assertEqual(
                visible_lines(terminal),
                ("", "", "0", "1", "2", "3", "4", "5", "6", "7"),
            )

    def test_scroll_down_never_pulls_rows_back_out_of_history(self):
        with Shitty(columns=3, rows=3, save_lines=2) as terminal:
            terminal.write(numbered_lines(0, 4))
            before_history = terminal.scrollback_state()[0]
            terminal.write(b"\x1b[2T")

            self.assertEqual(terminal.scrollback_state()[0], before_history)
            self.assertEqual(visible_lines(terminal), ("", "", "2"))
            terminal.wheel_up(10_000)
            self.assertEqual(visible_lines(terminal), ("0", "1", ""))

    def test_public_cell_iteration_is_row_major_across_line_boundaries(self):
        rows = (b"ABCDE", b"FGHIJ", b"KLMNO", b"PQRST", b"UVWXY")
        with Shitty(columns=5, rows=5, save_lines=0) as terminal:
            terminal.write(put_rows(*rows))
            snapshot = terminal.model_snapshot()

            self.assertEqual(
                "".join(cell.char for cell in snapshot.cells),
                "ABCDEFGHIJKLMNOPQRSTUVWXY",
            )
            self.assertEqual(snapshot.cell(4, 0).char, "E")
            self.assertEqual(snapshot.cell(0, 1).char, "F")

    def test_width_shrink_reflows_one_logical_line_into_history(self):
        with Shitty(columns=5, rows=1, save_lines=2) as terminal:
            terminal.write(b"12345")
            terminal.resize(2, 1)

            self.assertEqual(terminal.all_text(), ("12", "34", "5"))
            self.assertEqual(visible_lines(terminal), ("5",))
            self.assertEqual(terminal.scrollback_state()[0], 2)

    def test_two_width_shrinks_match_the_direct_reflow_result(self):
        with Shitty(columns=5, rows=1, save_lines=2) as direct:
            direct.write(b"12345")
            direct.resize(2, 1)
            expected = (direct.all_text(), direct.model_digest())

        with Shitty(columns=5, rows=1, save_lines=2) as incremental:
            incremental.write(b"12345")
            incremental.resize(4, 1)
            incremental.resize(2, 1)

            self.assertEqual(incremental.all_text(), expected[0])
            self.assertEqual(incremental.model_digest(), expected[1])

    def test_reflow_preserves_an_empty_cell_inside_a_logical_line(self):
        with Shitty(columns=5, rows=1, save_lines=4) as terminal:
            terminal.write(b"1\x1b[C34")
            terminal.resize(2, 1)
            self.assertEqual(terminal.all_text(), ("1", "34"))
            terminal.wheel_up()
            history = terminal.model_snapshot()
            self.assertEqual(
                (history.cell(0, 0).char, history.cell(1, 0).char),
                ("1", " "),
            )
            terminal.wheel_down()
            terminal.resize(1, 1)

            self.assertEqual(terminal.all_text(), ("1", "", "3", "4"))
            self.assertEqual(terminal.scrollback_state()[0], 3)

    def test_width_growth_unwraps_a_two_row_logical_line(self):
        with Shitty(columns=2, rows=2, save_lines=0) as terminal:
            terminal.write(b"123")
            terminal.resize(3, 2)

            self.assertEqual(visible_lines(terminal), ("123", ""))

    def test_width_growth_unwraps_multiple_rows_into_one_line(self):
        with Shitty(columns=2, rows=3, save_lines=0) as terminal:
            terminal.write(b"123456")
            terminal.resize(6, 3)

            self.assertEqual(visible_lines(terminal), ("123456", "", ""))

    def test_growth_without_reflow_keeps_alternate_screen_rows_separate(self):
        with Shitty(columns=2, rows=2, save_lines=0) as terminal:
            terminal.write(b"\x1b[?1049h123")
            terminal.resize(3, 2)

            self.assertEqual(visible_lines(terminal), ("12", "3"))

    def test_shrink_without_reflow_truncates_alternate_screen_columns(self):
        with Shitty(columns=5, rows=1, save_lines=0) as terminal:
            terminal.write(b"\x1b[?1049h12345")
            terminal.resize(2, 1)

            self.assertEqual(visible_lines(terminal), ("12",))

    def test_public_snapshot_cardinality_is_exact_at_every_coordinate(self):
        rows = (b"ABCDE", b"FGHIJ", b"KLMNO", b"PQRST", b"UVWXY")
        with Shitty(columns=5, rows=5, save_lines=2) as terminal:
            terminal.write(put_rows(*rows))
            snapshot = terminal.model_snapshot()

            self.assertEqual(len(snapshot.cells), snapshot.rows * snapshot.columns)
            for row in range(snapshot.rows):
                for column in range(snapshot.columns):
                    self.assertIs(
                        snapshot.cell(column, row),
                        snapshot.cells[row * snapshot.columns + column],
                    )


if __name__ == "__main__":
    unittest.main()
