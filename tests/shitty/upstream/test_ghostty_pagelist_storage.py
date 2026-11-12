# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty, put_rows


UPSTREAM_CASES = (
    "PageList Builder transfers mixed-width pages",
    "PageList Builder validates the finished list",
    "PageList Builder finish is transactional on allocation failure",
    "PageList PageAllocation finalizes pages and preserves live state",
    "PageList PageAllocation stays detached until finalize",
    "PageList PageAllocation rejects limits before modifying the destination",
    "PageList PageAllocation allocation failure leaves list unchanged",
    "PageList Pin row movement clamps across mixed-width pages",
    "PageList Pin wrapping crosses mixed-width pages",
    "PageList Pin rejects columns beyond mixed-width page bounds",
    "PageList Pin rightWrap exact row multiple",
    "PageList Pin leftWrap exact row multiple",
    "PageList Pin rightWrap maximum distance",
    "PageList Pin leftWrap maximum distance",
    "PageList incremental compression skips visible history",
    "PageList owns incremental compression state",
    "PageList replacements preserve compression continuation and mark activity",
    "PageList incremental compression bounds inspected pages",
    "PageList incremental compression advances after failure",
    "PageList incremental compression advances after allocation failure",
)


def visible_lines(terminal):
    return tuple(line.rstrip() for line in terminal.snapshot().lines)


def numbered_lines(first, last):
    return b"\r\n".join(str(value).encode() for value in range(first, last + 1))


def select(terminal, start, end):
    terminal.select_start(*start)
    terminal.select_update(*end)
    return terminal.select_finish()


class GhosttyPageListStorageTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 20)
        self.assertEqual(len(set(UPSTREAM_CASES)), 20)

    def test_rows_created_at_different_widths_keep_order_and_content(self):
        with Shitty(columns=2, rows=3, save_lines=8) as terminal:
            terminal.write(numbered_lines(1, 4))
            terminal.resize(4, 3)
            terminal.write(b"\r\nFIVE")

            self.assertEqual(terminal.all_text(), ("1", "2", "3", "4", "FIVE"))
            self.assertEqual(visible_lines(terminal), ("3", "4", "FIVE"))

    def test_invalid_finished_geometry_is_rejected(self):
        with Shitty(columns=4, rows=3, save_lines=3) as terminal:
            terminal.write(b"valid")
            before = terminal.model_digest()

            with self.assertRaises(RuntimeError):
                terminal.resize(0, 3)

            self.assertEqual(terminal.model_digest(), before)

    def test_failed_geometry_transaction_keeps_rich_state(self):
        with Shitty(columns=8, rows=3, save_lines=5) as terminal:
            terminal.write(
                b"\x1b[1;38;2;1;2;3m"
                b"\x1b]8;;https://example.test/transaction\x1b\\"
                b"state"
            )
            before = terminal.model_snapshot()

            with self.assertRaises(RuntimeError):
                terminal.resize(8, 0)

            self.assertEqual(terminal.model_snapshot(), before)
            self.assertEqual(
                terminal.hyperlink(0, 0),
                "https://example.test/transaction",
            )

    def test_history_growth_preserves_a_pinned_viewport(self):
        with Shitty(columns=8, rows=3, save_lines=20) as terminal:
            terminal.write(numbered_lines(1, 10))
            terminal.wheel_up(2)
            before = visible_lines(terminal)
            before_offset = terminal.snapshot().view_offset

            terminal.write(b"\r\n11\r\n12")

            self.assertEqual(visible_lines(terminal), before)
            self.assertEqual(terminal.snapshot().view_offset, before_offset + 2)
            self.assertEqual(terminal.all_text()[-2:], ("11", "12"))

    def test_unfinished_parser_payload_does_not_publish_a_cell(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.write(b"\x1b]8;;https://example.test/detached")
            self.assertEqual(visible_lines(terminal), ("", ""))
            self.assertEqual(terminal.hyperlink_count(), 0)

            terminal.write(b"\x1b\\X\x1b]8;;\x1b\\")
            self.assertEqual(visible_lines(terminal), ("X", ""))
            self.assertEqual(
                terminal.hyperlink(0, 0),
                "https://example.test/detached",
            )

    def test_history_limit_rejects_old_rows_before_exposing_spare_capacity(self):
        with Shitty(columns=6, rows=2, save_lines=3) as terminal:
            terminal.write(numbered_lines(0, 19))

            self.assertEqual(terminal.all_text(), ("15", "16", "17", "18", "19"))
            self.assertEqual(visible_lines(terminal), ("18", "19"))
            self.assertEqual(terminal.scrollback_state()[0], 3)

    def test_failed_resize_does_not_publish_partial_history_changes(self):
        with Shitty(columns=5, rows=3, save_lines=10) as terminal:
            terminal.write(numbered_lines(1, 8))
            terminal.wheel_up(2)
            before_model = terminal.model_snapshot()
            before_text = terminal.all_text()

            with self.assertRaises(RuntimeError):
                terminal.resize(0, 4)

            self.assertEqual(terminal.model_snapshot(), before_model)
            self.assertEqual(terminal.all_text(), before_text)

    def test_selection_pins_follow_rows_across_width_changes(self):
        data = b"abcdefghijklmnopqrstuvwxyz"
        with Shitty(columns=8, rows=4, save_lines=5) as terminal:
            terminal.write(data)
            terminal.select_start(6, 0)
            terminal.select_update(4, 2)
            before = terminal.selection_state()
            terminal.resize(5, 6)
            after = terminal.selection_state()

            self.assertNotEqual(after["raw"], before["raw"])
            self.assertEqual(terminal.select_finish(), b"ghijklmnopqrst")

    def test_selection_pins_cross_multiple_reflow_widths(self):
        data = b"0123456789abcdefghijklmnopqrst"
        with Shitty(columns=4, rows=5, save_lines=10) as terminal:
            terminal.write(data)
            terminal.select_start(1, 1)
            terminal.select_update(2, 4)
            expected = terminal.select_finish()

            terminal.select_start(1, 1)
            terminal.select_update(2, 4)
            terminal.resize(7, 5)
            terminal.resize(3, 7)

            self.assertEqual(terminal.select_finish(), expected)

    def test_public_selection_clamps_coordinates_beyond_page_bounds(self):
        with Shitty(columns=10, rows=3, save_lines=0) as terminal:
            terminal.write(put_rows(b"0123456789", b"abcdefghij", b"ABCDEFGHIJ"))

            terminal.select_start(0, 0)
            terminal.select_update(1_000_000, 1_000_000)
            state = terminal.selection_state()

            self.assertEqual(state["raw"], (0, 0, 10, 2))
            self.assertEqual(
                terminal.select_finish(),
                b"0123456789\nabcdefghij\nABCDEFGHIJ",
            )

    def test_linear_extent_wraps_right_by_an_exact_row_multiple(self):
        with Shitty(columns=10, rows=3, save_lines=0) as terminal:
            terminal.write(b"0123456789abcdefghijABCDEFGHIJ")

            self.assertEqual(select(terminal, (5, 0), (9, 1)), b"56789abcdefghi")

    def test_linear_extent_wraps_left_by_an_exact_row_multiple(self):
        with Shitty(columns=10, rows=3, save_lines=0) as terminal:
            terminal.write(b"0123456789abcdefghijABCDEFGHIJ")

            self.assertEqual(select(terminal, (0, 1), (5, 2)), b"abcdefghijABCDE")

    def test_maximum_right_coordinate_is_bounded_by_the_page(self):
        with Shitty(columns=1, rows=3, save_lines=0) as terminal:
            terminal.write(put_rows(b"A", b"B", b"C"))

            terminal.select_start(0, 0)
            terminal.select_update(1_000_000, 1_000_000)

            self.assertEqual(terminal.selection_state()["raw"], (0, 0, 1, 2))
            self.assertEqual(terminal.select_finish(), b"A\nB\nC")

    def test_maximum_leftward_extent_is_bounded_by_the_page(self):
        with Shitty(columns=1, rows=3, save_lines=0) as terminal:
            terminal.write(put_rows(b"A", b"B", b"C"))

            terminal.select_start(1_000_000, 1_000_000)
            terminal.select_update(0, 0)

            self.assertEqual(terminal.selection_state()["raw"], (0, 0, 1, 2))
            self.assertEqual(terminal.select_finish(), b"A\nB\nC")

    def test_visible_history_survives_cold_storage_navigation(self):
        with Shitty(columns=8, rows=4, save_lines=300) as terminal:
            terminal.write(numbered_lines(0, 199))
            terminal.wheel_up(10_000)

            self.assertEqual(visible_lines(terminal), ("0", "1", "2", "3"))
            terminal.wheel_down(1)
            self.assertEqual(visible_lines(terminal), ("1", "2", "3", "4"))
            terminal.wheel_down(10_000)
            self.assertEqual(visible_lines(terminal), ("196", "197", "198", "199"))

    def test_sessions_own_independent_history_navigation_state(self):
        with Shitty(columns=6, rows=3, save_lines=20) as first:
            with Shitty(columns=6, rows=3, save_lines=20) as second:
                first.write(numbered_lines(1, 10))
                second.write(numbered_lines(101, 110))
                first.wheel_up(3)

                self.assertEqual(visible_lines(first), ("5", "6", "7"))
                self.assertEqual(visible_lines(second), ("108", "109", "110"))
                self.assertEqual(second.snapshot().view_offset, 0)

    def test_storage_replacement_preserves_selection_style_and_link(self):
        uri = "https://example.test/replacement"
        with Shitty(columns=6, rows=4, save_lines=120) as terminal:
            terminal.write(numbered_lines(0, 79) + b"\r\n")
            terminal.write(
                b"\x1b[1m\x1b]8;;" + uri.encode() + b"\x1b\\linked"
            )
            terminal.select_start(0, 3)
            terminal.select_update(6, 3)
            terminal.resize(12, 4)
            snapshot = terminal.snapshot()

            self.assertEqual(terminal.select_finish(), b"linked")
            self.assertTrue(snapshot.cell(0, 3).bold)
            self.assertEqual(terminal.hyperlink(0, 3), uri)

    def test_large_history_navigation_remains_bounded_and_exact(self):
        with Shitty(columns=8, rows=5, save_lines=1000) as terminal:
            terminal.write(numbered_lines(0, 999))
            terminal.wheel_up(37)
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.view_offset, 37)
            self.assertEqual(visible_lines(terminal), ("958", "959", "960", "961", "962"))
            self.assertEqual(len(snapshot.cells), 40)

    def test_recoverable_failure_does_not_stall_history_navigation(self):
        with Shitty(columns=8, rows=3, save_lines=40) as terminal:
            terminal.write(numbered_lines(1, 20))
            with self.assertRaises(RuntimeError):
                terminal.resize(0, 3)

            terminal.wheel_up(4)
            self.assertEqual(visible_lines(terminal), ("14", "15", "16"))
            terminal.wheel_down(4)
            self.assertEqual(visible_lines(terminal), ("18", "19", "20"))

    def test_recoverable_failure_does_not_block_later_storage_growth(self):
        with Shitty(columns=8, rows=3, save_lines=20) as terminal:
            terminal.write(b"before")
            with self.assertRaises(RuntimeError):
                terminal.resize(8, 0)

            terminal.write(b"\r\n" + numbered_lines(1, 30))

            self.assertEqual(visible_lines(terminal), ("28", "29", "30"))
            self.assertEqual(terminal.scrollback_state()[0], 20)


if __name__ == "__main__":
    unittest.main()
