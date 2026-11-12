# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


UPSTREAM_CASES = (
    "PageList scroll with max_size 0 no history",
    "PageList scroll top",
    "PageList scroll delta row back",
    "PageList scroll delta row back overflow",
    "PageList scroll minimum row delta",
    "PageList scroll delta row forward",
    "PageList scroll delta row forward into active",
    "PageList scroll delta row back without space preserves active",
    "PageList scroll to pin",
    "PageList scroll to pin in active",
    "PageList scroll to pin at top",
    "PageList scroll to row 0",
    "PageList scroll to row in scrollback",
    "PageList scroll to row in middle",
    "PageList scroll to row at active boundary",
    "PageList scroll to row beyond active",
    "PageList scroll to row without scrollback",
    "PageList scroll to row then delta",
    "PageList scroll to row with cache fast path down",
    "PageList scroll to row with cache fast path up",
)


def numbered_lines(first, last, width=3):
    return b"\r\n".join(
        str(value).zfill(width).encode()
        for value in range(first, last + 1)
    )


def visible_lines(terminal):
    return tuple(line.rstrip() for line in terminal.snapshot().lines)


class GhosttyPageListScrollTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 20)
        self.assertEqual(len(set(UPSTREAM_CASES)), 20)

    def test_zero_history_budget_rejects_every_backward_scroll(self):
        with Shitty(columns=8, rows=4, save_lines=0) as terminal:
            terminal.write(numbered_lines(0, 12))
            before = visible_lines(terminal)

            terminal.wheel_up(10)
            terminal.page_up()

            self.assertEqual(visible_lines(terminal), before)
            self.assertEqual(terminal.snapshot().view_offset, 0)
            self.assertEqual(terminal.scrollback_state(), (0, 4, 4, 0))

    def test_top_view_remains_anchored_until_returning_to_live_output(self):
        with Shitty(columns=8, rows=4, save_lines=50) as terminal:
            terminal.write(numbered_lines(0, 9))
            terminal.wheel_up(100)
            self.assertEqual(visible_lines(terminal), ("000", "001", "002", "003"))
            self.assertEqual(terminal.scrollback_state(), (6, 10, 4, 0))

            terminal.write(b"\r\n010")
            self.assertEqual(visible_lines(terminal), ("000", "001", "002", "003"))
            self.assertEqual(terminal.scrollback_state(), (7, 11, 4, 0))

            terminal.wheel_down(100)
            self.assertEqual(visible_lines(terminal), ("007", "008", "009", "010"))
            self.assertEqual(terminal.scrollback_state(), (7, 11, 4, 7))

    def test_one_row_back_preserves_its_absolute_anchor_during_output(self):
        with Shitty(columns=8, rows=4, save_lines=50) as terminal:
            terminal.write(numbered_lines(0, 9))
            terminal.wheel_up(1)

            self.assertEqual(visible_lines(terminal), ("005", "006", "007", "008"))
            self.assertEqual(terminal.scrollback_state(), (6, 10, 4, 5))

            terminal.write(b"\r\n010")
            self.assertEqual(visible_lines(terminal), ("005", "006", "007", "008"))
            self.assertEqual(terminal.scrollback_state(), (7, 11, 4, 5))

            terminal.wheel_up(1)
            self.assertEqual(terminal.scrollback_state(), (7, 11, 4, 4))

    def test_backward_overflow_clamps_to_top_and_stays_there(self):
        with Shitty(columns=8, rows=4, save_lines=50) as terminal:
            terminal.write(numbered_lines(0, 9))
            terminal.wheel_up(100)

            self.assertEqual(terminal.snapshot().view_offset, 6)
            self.assertEqual(terminal.scrollback_state(), (6, 10, 4, 0))
            terminal.write(b"\r\n010")
            self.assertEqual(terminal.snapshot().view_offset, 7)
            self.assertEqual(terminal.scrollback_state(), (7, 11, 4, 0))

    def test_extreme_single_scroll_event_saturates_at_oldest_row(self):
        with Shitty(columns=8, rows=4, save_lines=50) as terminal:
            terminal.write(numbered_lines(0, 19))

            terminal.scroll(0, 1000)

            self.assertEqual(visible_lines(terminal), ("000", "001", "002", "003"))
            self.assertEqual(terminal.scrollback_state(), (16, 20, 4, 0))

    def test_forward_delta_from_top_moves_exactly_two_rows(self):
        with Shitty(columns=8, rows=4, save_lines=50) as terminal:
            terminal.write(numbered_lines(0, 9))
            terminal.wheel_up(100)
            terminal.wheel_down(2)

            self.assertEqual(visible_lines(terminal), ("002", "003", "004", "005"))
            self.assertEqual(terminal.scrollback_state(), (6, 10, 4, 2))

            terminal.write(b"\r\n010")
            self.assertEqual(visible_lines(terminal), ("002", "003", "004", "005"))
            self.assertEqual(terminal.scrollback_state(), (7, 11, 4, 2))

    def test_forward_delta_at_live_output_is_a_noop(self):
        with Shitty(columns=8, rows=4, save_lines=50) as terminal:
            terminal.write(numbered_lines(0, 9))
            before = visible_lines(terminal)

            terminal.wheel_down(2)

            self.assertEqual(visible_lines(terminal), before)
            self.assertEqual(terminal.snapshot().view_offset, 0)
            self.assertEqual(terminal.scrollback_state(), (6, 10, 4, 6))

    def test_backward_delta_without_history_preserves_live_view(self):
        with Shitty(columns=8, rows=4, save_lines=20) as terminal:
            before = terminal.model_digest()

            terminal.wheel_up(1)

            self.assertEqual(terminal.model_digest(), before)
            self.assertEqual(terminal.snapshot().view_offset, 0)
            self.assertEqual(terminal.scrollback_state(), (0, 4, 4, 0))

    def test_scrolling_to_two_history_anchors_updates_absolute_offset(self):
        with Shitty(columns=8, rows=4, save_lines=50) as terminal:
            terminal.write(numbered_lines(0, 13))
            terminal.wheel_up(6)
            self.assertEqual(visible_lines(terminal), ("004", "005", "006", "007"))
            self.assertEqual(terminal.scrollback_state(), (10, 14, 4, 4))

            terminal.wheel_down(1)
            self.assertEqual(visible_lines(terminal), ("005", "006", "007", "008"))
            self.assertEqual(terminal.scrollback_state(), (10, 14, 4, 5))

    def test_scrolling_past_an_active_pin_selects_live_output(self):
        with Shitty(columns=8, rows=4, save_lines=50) as terminal:
            terminal.write(numbered_lines(0, 13))
            terminal.wheel_up(8)
            terminal.wheel_down(100)

            self.assertEqual(visible_lines(terminal), ("010", "011", "012", "013"))
            self.assertEqual(terminal.snapshot().view_offset, 0)
            self.assertEqual(terminal.scrollback_state(), (10, 14, 4, 10))

    def test_oldest_history_anchor_has_zero_absolute_offset(self):
        with Shitty(columns=8, rows=4, save_lines=50) as terminal:
            terminal.write(numbered_lines(0, 13))
            terminal.wheel_up(10)

            self.assertEqual(visible_lines(terminal), ("000", "001", "002", "003"))
            self.assertEqual(terminal.scrollback_state(), (10, 14, 4, 0))

    def test_page_navigation_reaches_row_zero_and_keeps_it_anchored(self):
        with Shitty(columns=8, rows=4, save_lines=80) as terminal:
            terminal.write(numbered_lines(0, 29))
            for _ in range(20):
                terminal.page_up()

            self.assertEqual(visible_lines(terminal), ("000", "001", "002", "003"))
            self.assertEqual(terminal.scrollback_state(), (26, 30, 4, 0))
            terminal.write(b"\r\n030")
            self.assertEqual(visible_lines(terminal), ("000", "001", "002", "003"))

    def test_history_row_anchor_survives_later_output(self):
        with Shitty(columns=8, rows=4, save_lines=80) as terminal:
            terminal.write(numbered_lines(0, 43))
            terminal.wheel_up(35)

            self.assertEqual(visible_lines(terminal), ("005", "006", "007", "008"))
            self.assertEqual(terminal.scrollback_state(), (40, 44, 4, 5))
            terminal.write(b"\r\n044")
            self.assertEqual(visible_lines(terminal), ("005", "006", "007", "008"))
            self.assertEqual(terminal.scrollback_state(), (41, 45, 4, 5))

    def test_middle_history_anchor_survives_later_output(self):
        with Shitty(columns=8, rows=4, save_lines=80) as terminal:
            terminal.write(numbered_lines(0, 53))
            terminal.wheel_up(23)

            self.assertEqual(visible_lines(terminal), ("027", "028", "029", "030"))
            self.assertEqual(terminal.scrollback_state(), (50, 54, 4, 27))
            terminal.write(b"\r\n054")
            self.assertEqual(visible_lines(terminal), ("027", "028", "029", "030"))
            self.assertEqual(terminal.scrollback_state(), (51, 55, 4, 27))

    def test_live_boundary_follows_output_as_history_grows(self):
        with Shitty(columns=8, rows=4, save_lines=80) as terminal:
            terminal.write(numbered_lines(0, 23))
            self.assertEqual(terminal.scrollback_state(), (20, 24, 4, 20))

            terminal.write(b"\r\n024")

            self.assertEqual(visible_lines(terminal), ("021", "022", "023", "024"))
            self.assertEqual(terminal.snapshot().view_offset, 0)
            self.assertEqual(terminal.scrollback_state(), (21, 25, 4, 21))

    def test_forward_overflow_beyond_active_clamps_to_live_output(self):
        with Shitty(columns=8, rows=4, save_lines=80) as terminal:
            terminal.write(numbered_lines(0, 13))
            terminal.wheel_up(4)
            terminal.wheel_down(100)

            self.assertEqual(visible_lines(terminal), ("010", "011", "012", "013"))
            self.assertEqual(terminal.scrollback_state(), (10, 14, 4, 10))

    def test_page_navigation_without_scrollback_stays_live(self):
        with Shitty(columns=8, rows=4, save_lines=0) as terminal:
            for _ in range(4):
                terminal.page_up()
                terminal.page_down()

            self.assertEqual(terminal.snapshot().view_offset, 0)
            self.assertEqual(terminal.scrollback_state(), (0, 4, 4, 0))

    def test_history_anchor_accepts_forward_and_backward_deltas(self):
        with Shitty(columns=8, rows=4, save_lines=80) as terminal:
            terminal.write(numbered_lines(0, 33))
            terminal.wheel_up(20)
            self.assertEqual(terminal.scrollback_state(), (30, 34, 4, 10))

            terminal.wheel_down(5)
            self.assertEqual(visible_lines(terminal), ("015", "016", "017", "018"))
            self.assertEqual(terminal.scrollback_state(), (30, 34, 4, 15))

            terminal.wheel_up(3)
            self.assertEqual(visible_lines(terminal), ("012", "013", "014", "015"))
            self.assertEqual(terminal.scrollback_state(), (30, 34, 4, 12))

    def test_repeated_row_navigation_down_keeps_cached_anchor_stable(self):
        with Shitty(columns=8, rows=4, save_lines=100) as terminal:
            terminal.write(numbered_lines(0, 53))
            terminal.wheel_up(40)
            self.assertEqual(terminal.scrollback_state(), (50, 54, 4, 10))

            terminal.wheel_down(10)
            self.assertEqual(visible_lines(terminal), ("020", "021", "022", "023"))
            terminal.write(b"\r\n054")
            self.assertEqual(visible_lines(terminal), ("020", "021", "022", "023"))
            self.assertEqual(terminal.scrollback_state(), (51, 55, 4, 20))

    def test_repeated_row_navigation_up_keeps_cached_anchor_stable(self):
        with Shitty(columns=8, rows=4, save_lines=100) as terminal:
            terminal.write(numbered_lines(0, 53))
            terminal.wheel_up(20)
            self.assertEqual(terminal.scrollback_state(), (50, 54, 4, 30))

            terminal.wheel_up(15)
            self.assertEqual(visible_lines(terminal), ("015", "016", "017", "018"))
            terminal.write(b"\r\n054")
            self.assertEqual(visible_lines(terminal), ("015", "016", "017", "018"))
            self.assertEqual(terminal.scrollback_state(), (51, 55, 4, 15))


if __name__ == "__main__":
    unittest.main()
