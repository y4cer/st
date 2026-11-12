# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


UPSTREAM_CASES = (
    "PageList incremental compression advances after decommit failure",
    "PageList incremental compression restarts after replacement",
    "PageList incremental compression restarts after reset",
    "PageList incremental compression restarts after active boundary resize",
    "PageList incremental compression restarts after prune reuse",
    "PageList bounded pruning after partial erase preserves live serials",
    "PageList partial erase restarts compression before continuation",
    "PageList bounded pruning after split invalidation preserves live serials",
    "PageList repeated bounded pruning after split preserves live serials",
    "PageList bounded pruning after front replacement preserves live serials",
    "PageList bounded pruning after middle replacement preserves live serials",
    "PageList incremental compression restarts after earlier replacement",
    "PageList incremental compression keeps progress after tail growth",
    "PageList memory stats do not restore compressed pages",
    "PageList preserved page keeps compressed storage",
    "PageList memory stats include unused pool backing",
    "PageList does not compress the mixed history and active page",
    "PageList compresses only complete cold history pages",
    "PageList lazily restores compressed history made active by resize",
    "PageList full and incremental compression skip a spanning viewport",
)


def numbered_lines(first, last, width=0):
    values = []
    for value in range(first, last + 1):
        text = str(value)
        if width:
            text = text.zfill(width)
        values.append(text.encode())
    return b"\r\n".join(values)


def visible_lines(terminal):
    return tuple(line.rstrip() for line in terminal.snapshot().lines)


class GhosttyPageListCompressionTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 20)
        self.assertEqual(len(set(UPSTREAM_CASES)), 20)

    def test_recoverable_reclamation_failure_does_not_stall_later_history(self):
        with Shitty(columns=8, rows=3, save_lines=30) as terminal:
            terminal.write(numbered_lines(1, 15))
            with self.assertRaises(RuntimeError):
                terminal.resize(0, 3)
            terminal.write(b"\r\n" + numbered_lines(16, 20))

            self.assertEqual(visible_lines(terminal), ("18", "19", "20"))
            terminal.wheel_up(17)
            self.assertEqual(visible_lines(terminal), ("1", "2", "3"))

    def test_reflow_replacement_preserves_oldest_and_newest_rows(self):
        with Shitty(columns=6, rows=4, save_lines=120) as terminal:
            terminal.write(numbered_lines(0, 99, width=3))
            terminal.resize(12, 4)

            self.assertEqual(visible_lines(terminal), ("096", "097", "098", "099"))
            terminal.wheel_up(10_000)
            self.assertEqual(visible_lines(terminal), ("000", "001", "002", "003"))

    def test_hard_reset_discards_old_storage_and_accepts_new_history(self):
        with Shitty(columns=8, rows=3, save_lines=10) as terminal:
            terminal.write(numbered_lines(1, 12))
            terminal.write(b"\x1bc")
            terminal.write(numbered_lines(101, 106))

            self.assertEqual(visible_lines(terminal), ("104", "105", "106"))
            self.assertNotIn("12", terminal.all_text())
            self.assertEqual(terminal.all_text(), ("101", "102", "103", "104", "105", "106"))

    def test_active_boundary_growth_and_shrink_preserve_content(self):
        with Shitty(columns=6, rows=3, save_lines=10) as terminal:
            terminal.write(numbered_lines(1, 8))
            terminal.resize(6, 8)
            self.assertEqual(visible_lines(terminal), ("1", "2", "3", "4", "5", "6", "7", "8"))

            terminal.resize(6, 3)
            self.assertEqual(visible_lines(terminal), ("6", "7", "8"))
            self.assertEqual(terminal.all_text(), ("1", "2", "3", "4", "5", "6", "7", "8"))

    def test_bounded_history_reuses_storage_without_exposing_old_rows(self):
        with Shitty(columns=8, rows=3, save_lines=4) as terminal:
            terminal.write(numbered_lines(0, 100))

            self.assertEqual(terminal.all_text(), ("94", "95", "96", "97", "98", "99", "100"))
            self.assertEqual(visible_lines(terminal), ("98", "99", "100"))

    def test_clear_history_preserves_live_rows_after_partial_erase(self):
        with Shitty(columns=8, rows=3, save_lines=20) as terminal:
            terminal.write(numbered_lines(1, 10))
            terminal.write(b"\x1b[3J")

            self.assertEqual(terminal.all_text(), ("8", "9", "10"))
            self.assertEqual(visible_lines(terminal), ("8", "9", "10"))

    def test_clear_history_while_scrolled_restarts_at_live_content(self):
        with Shitty(columns=8, rows=3, save_lines=20) as terminal:
            terminal.write(numbered_lines(1, 10))
            terminal.wheel_up(3)
            terminal.write(b"\x1b[3J")
            terminal.write(b"\r\n11")

            self.assertEqual(terminal.snapshot().view_offset, 0)
            self.assertEqual(visible_lines(terminal), ("9", "10", "11"))

    def test_width_split_with_bounded_history_keeps_complete_graphemes(self):
        with Shitty(columns=8, rows=3, save_lines=8) as terminal:
            terminal.write(("ab😀cd\r\n" * 10 + "tail😀").encode())
            terminal.resize(4, 3)
            snapshot = terminal.snapshot()

            for row in range(snapshot.rows):
                for column in range(snapshot.columns):
                    cell = snapshot.cell(column, row)
                    if cell.double_width:
                        self.assertLess(column + 1, snapshot.columns)
                        self.assertTrue(
                            snapshot.cell(column + 1, row).double_width_continuation
                        )
            self.assertIn("😀", "".join(visible_lines(terminal)))

    def test_repeated_split_and_prune_keeps_the_newest_logical_lines(self):
        with Shitty(columns=9, rows=3, save_lines=6) as terminal:
            terminal.write(numbered_lines(0, 30, width=3))
            for columns in (4, 11, 5, 9):
                terminal.resize(columns, 3)

            self.assertEqual(visible_lines(terminal), ("028", "029", "030"))
            self.assertLessEqual(terminal.scrollback_state()[0], 6)

    def test_front_pruning_does_not_change_current_rendition(self):
        with Shitty(columns=8, rows=3, save_lines=5) as terminal:
            terminal.write(numbered_lines(0, 20) + b"\r\n\x1b[1;3mcurrent")
            terminal.write(b"\r\nnext")
            snapshot = terminal.snapshot()

            self.assertTrue(snapshot.cell(0, 1).bold)
            self.assertTrue(snapshot.cell(0, 1).italic)
            self.assertTrue(snapshot.cell(0, 2).bold)
            self.assertTrue(snapshot.cell(0, 2).italic)

    def test_middle_replacement_preserves_a_live_selection(self):
        with Shitty(columns=8, rows=4, save_lines=20) as terminal:
            terminal.write(numbered_lines(1, 12, width=2))
            terminal.select_start(0, 1)
            terminal.select_update(2, 2)
            expected = terminal.select_finish()

            terminal.select_start(0, 1)
            terminal.select_update(2, 2)
            terminal.resize(5, 4)

            self.assertEqual(terminal.select_finish(), expected)

    def test_earlier_history_replacement_remains_navigable(self):
        with Shitty(columns=5, rows=3, save_lines=80) as terminal:
            terminal.write(numbered_lines(0, 59, width=2))
            terminal.resize(9, 3)
            terminal.wheel_up(10_000)

            self.assertEqual(visible_lines(terminal), ("00", "01", "02"))
            terminal.wheel_down(10_000)
            self.assertEqual(visible_lines(terminal), ("57", "58", "59"))

    def test_tail_growth_keeps_a_parked_viewport_on_the_same_rows(self):
        with Shitty(columns=8, rows=4, save_lines=40) as terminal:
            terminal.write(numbered_lines(1, 20))
            terminal.wheel_up(7)
            before = visible_lines(terminal)
            terminal.write(b"\r\n" + numbered_lines(21, 25))

            self.assertEqual(visible_lines(terminal), before)
            self.assertEqual(terminal.all_text()[-1], "25")

    def test_storage_metadata_queries_do_not_change_the_model(self):
        with Shitty(columns=8, rows=4, save_lines=60) as terminal:
            terminal.write(numbered_lines(1, 50))
            before = terminal.model_digest()
            before_text = terminal.all_text()

            for _ in range(32):
                terminal.scrollback_state()

            self.assertEqual(terminal.model_digest(), before)
            self.assertEqual(terminal.all_text(), before_text)

    def test_preserved_model_snapshots_do_not_change_cold_history(self):
        with Shitty(columns=8, rows=4, save_lines=60) as terminal:
            terminal.write(numbered_lines(1, 50))
            terminal.wheel_up(25)
            before = terminal.model_digest()
            before_view = visible_lines(terminal)

            for _ in range(16):
                terminal.model_snapshot()

            self.assertEqual(terminal.model_digest(), before)
            self.assertEqual(visible_lines(terminal), before_view)

    def test_logical_history_limit_ignores_unused_backing_capacity(self):
        with Shitty(columns=8, rows=3, save_lines=7) as terminal:
            terminal.write(numbered_lines(0, 99))

            self.assertEqual(terminal.scrollback_state()[0], 7)
            self.assertEqual(len(terminal.all_text()), 10)
            self.assertEqual(terminal.all_text()[0], "90")

    def test_history_prefix_sharing_live_storage_remains_readable(self):
        with Shitty(columns=8, rows=4, save_lines=4) as terminal:
            terminal.write(numbered_lines(1, 5))
            terminal.wheel_up(1)

            self.assertEqual(visible_lines(terminal), ("1", "2", "3", "4"))
            terminal.wheel_down(1)
            self.assertEqual(visible_lines(terminal), ("2", "3", "4", "5"))

    def test_complete_cold_history_and_live_rows_stay_distinct(self):
        with Shitty(columns=8, rows=5, save_lines=200) as terminal:
            terminal.write(numbered_lines(0, 149, width=3))
            bottom = visible_lines(terminal)
            terminal.wheel_up(100)
            history = visible_lines(terminal)

            self.assertEqual(bottom, ("145", "146", "147", "148", "149"))
            self.assertEqual(history, ("045", "046", "047", "048", "049"))
            terminal.wheel_down(100)
            self.assertEqual(visible_lines(terminal), bottom)

    def test_history_made_active_by_height_growth_is_restored_on_demand(self):
        with Shitty(columns=8, rows=3, save_lines=10) as terminal:
            terminal.write(numbered_lines(1, 8))
            terminal.resize(8, 8)

            self.assertEqual(visible_lines(terminal), ("1", "2", "3", "4", "5", "6", "7", "8"))
            self.assertEqual(terminal.snapshot().cell(0, 0).char, "1")

    def test_viewport_spanning_storage_boundaries_is_stable(self):
        with Shitty(columns=8, rows=7, save_lines=200) as terminal:
            terminal.write(numbered_lines(0, 119, width=3))
            terminal.wheel_up(53)
            before = visible_lines(terminal)
            before_state = terminal.scrollback_state()

            for _ in range(8):
                self.assertEqual(visible_lines(terminal), before)
                self.assertEqual(terminal.scrollback_state(), before_state)


if __name__ == "__main__":
    unittest.main()
