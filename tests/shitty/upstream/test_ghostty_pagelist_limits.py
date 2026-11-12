# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


UPSTREAM_CASES = (
    "PageList scroll clear",
    "PageList: jump zero prompts",
    "PageList: jump minimum prompt delta",
    "Screen: jump back one prompt",
    "Screen: jump forward prompt skips multiline continuation",
    "PageList grow fit in capacity",
    "PageList grow allocate",
    "PageList Cell screenPoint supports long scrollback",
    "PageList set max bytes prunes immediately and can be raised",
    "PageList set max bytes zero preserves active boundary",
    "PageList set max lines prunes immediately and can be raised",
    "PageList set max limits remain independent",
    "PageList max lines uses one-page minimum",
    "PageList max lines does not round larger limits",
    "PageList max lines and max size enforce the smaller limit",
    "PageList max lines applies to resize and clone",
    "PageList grow prune scrollback",
    "PageList grow prune scrollback with viewport pin not in pruned page",
    "PageList eraseRows invalidates viewport offset cache",
    "PageList eraseRow invalidates viewport offset cache",
)


PROMPT_PREVIOUS_KEY = 265
PROMPT_NEXT_KEY = 264
PRESS = 1
RELEASE = 0
CONTROL_SHIFT = 1 | 2


def numbered_lines(first, last, width=3):
    return b"\r\n".join(
        str(value).zfill(width).encode()
        for value in range(first, last + 1)
    )


def visible_lines(terminal):
    return tuple(line.rstrip() for line in terminal.snapshot().lines)


def osc133(action):
    return b"\x1b]133;" + action + b"\x1b\\"


def prompt_key(terminal, key):
    terminal.frontend_key_event(key, PRESS, modifiers=CONTROL_SHIFT)
    terminal.frontend_key_event(key, RELEASE)


class GhosttyPageListLimitsTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 20)
        self.assertEqual(len(set(UPSTREAM_CASES)), 20)

    @unittest.expectedFailure
    def test_scroll_complete_moves_written_rows_into_history(self):
        with Shitty(columns=8, rows=3, save_lines=10) as terminal:
            terminal.write(b"A\r\nB\x1b[22J")

            self.assertEqual(visible_lines(terminal), ("", "", ""))
            self.assertEqual(
                (terminal.snapshot().cursor_x, terminal.snapshot().cursor_y),
                (0, 0),
            )
            self.assertEqual(terminal.scrollback_state(), (2, 5, 3, 2))
            terminal.wheel_up(2)
            self.assertEqual(visible_lines(terminal), ("A", "B", ""))

    def test_zero_delta_with_prompt_marks_is_a_true_noop(self):
        with Shitty(columns=8, rows=3, save_lines=20) as terminal:
            terminal.write(
                osc133(b"A") + b"old\r\n"
                + osc133(b"C") + b"output\r\nmore\r\n"
                + osc133(b"A") + b"new"
            )
            before_digest = terminal.model_digest()
            before_scrollbar = terminal.scrollback_state()

            terminal.scroll(0, 0)

            self.assertEqual(terminal.model_digest(), before_digest)
            self.assertEqual(terminal.scrollback_state(), before_scrollbar)

    @unittest.expectedFailure
    def test_prompt_previous_on_empty_history_is_bounded_and_consumed(self):
        with Shitty(columns=8, rows=3, save_lines=20) as terminal:
            prompt_key(terminal, PROMPT_PREVIOUS_KEY)

            self.assertEqual(terminal.snapshot().view_offset, 0)
            self.assertEqual(terminal.read_input(), b"")

    @unittest.expectedFailure
    def test_prompt_previous_jumps_to_the_prior_prompt_start(self):
        with Shitty(columns=8, rows=3, save_lines=20) as terminal:
            terminal.write(
                osc133(b"A") + b"old"
                + osc133(b"B") + b"\r\n"
                + osc133(b"C") + b"out1\r\nout2\r\nout3"
                + osc133(b"D") + b"\r\n"
                + osc133(b"A") + b"new"
            )
            prompt_key(terminal, PROMPT_PREVIOUS_KEY)

            self.assertEqual(terminal.scrollback_state()[3], 0)
            self.assertEqual(visible_lines(terminal)[0], "old")
            self.assertEqual(terminal.read_input(), b"")

    @unittest.expectedFailure
    def test_prompt_next_skips_prompt_continuation_rows(self):
        with Shitty(columns=8, rows=3, save_lines=20) as terminal:
            terminal.write(
                osc133(b"A") + b"old\r\ncont1\r\ncont2"
                + osc133(b"C") + b"\r\nout1\r\nout2"
                + osc133(b"D") + b"\r\n"
                + osc133(b"A") + b"next"
                + osc133(b"C") + b"\r\nlast1\r\nlast2\r\nlast3"
            )
            terminal.wheel_up(100)
            self.assertEqual(terminal.scrollback_state()[3], 0)

            prompt_key(terminal, PROMPT_NEXT_KEY)

            self.assertEqual(terminal.scrollback_state()[3], 5)
            self.assertEqual(visible_lines(terminal)[0], "next")
            self.assertEqual(terminal.read_input(), b"")

    def test_growth_inside_existing_storage_preserves_the_active_page(self):
        with Shitty(columns=8, rows=4, save_lines=0) as terminal:
            terminal.write(b"A\r\nB\r\nC\r\nD")

            self.assertEqual(visible_lines(terminal), ("A", "B", "C", "D"))
            self.assertEqual(terminal.scrollback_state(), (0, 4, 4, 0))

    def test_growth_across_storage_boundaries_preserves_every_row(self):
        with Shitty(columns=8, rows=5, save_lines=600) as terminal:
            terminal.write(numbered_lines(0, 399))
            contents = terminal.all_text()

            self.assertEqual(len(contents), 400)
            self.assertEqual(contents[0], "000")
            self.assertEqual(contents[-1], "399")
            self.assertEqual(terminal.scrollback_state(), (395, 400, 5, 395))

    def test_public_scrollbar_supports_more_than_u16_rows(self):
        with Shitty(columns=6, rows=16_000, save_lines=50_000) as terminal:
            terminal.write(numbered_lines(0, 65_999, width=5))

            self.assertEqual(
                terminal.scrollback_state(),
                (50_000, 66_000, 16_000, 50_000),
            )
            for _ in range(7):
                terminal.page_up()
            self.assertEqual(terminal.scrollback_state()[3], 0)
            terminal.page_down()
            self.assertEqual(terminal.scrollback_state()[3], 8_000)

    def test_different_history_budgets_prune_and_retain_exactly(self):
        with Shitty(columns=8, rows=3, save_lines=4) as small:
            small.write(numbered_lines(0, 19))
            self.assertEqual(small.all_text(), tuple(f"{n:03}" for n in range(13, 20)))

        with Shitty(columns=8, rows=3, save_lines=20) as large:
            large.write(numbered_lines(0, 19))
            self.assertEqual(large.all_text(), tuple(f"{n:03}" for n in range(20)))

    def test_zero_history_budget_preserves_only_the_active_boundary(self):
        with Shitty(columns=8, rows=3, save_lines=0) as terminal:
            terminal.write(numbered_lines(0, 19))

            self.assertEqual(terminal.all_text(), ("017", "018", "019"))
            self.assertEqual(terminal.scrollback_state(), (0, 3, 3, 0))
            terminal.wheel_up(100)
            self.assertEqual(visible_lines(terminal), ("017", "018", "019"))

    def test_line_budget_prunes_to_the_newest_exact_limit(self):
        with Shitty(columns=8, rows=3, save_lines=6) as terminal:
            terminal.write(numbered_lines(0, 29))

            self.assertEqual(terminal.scrollback_state(), (6, 9, 3, 6))
            self.assertEqual(terminal.all_text(), tuple(f"{n:03}" for n in range(21, 30)))

    def test_history_line_limit_is_independent_of_cell_extras(self):
        with Shitty(columns=8, rows=3, save_lines=8) as terminal:
            payload = bytearray()
            for index in range(20):
                uri = f"https://example.test/{index}/".encode() + b"x" * 256
                payload.extend(b"\x1b]8;;" + uri + b"\x1b\\")
                payload.extend(f"{index:03}".encode())
                payload.extend(b"\x1b]8;;\x1b\\\r\n")
            payload.extend(b"020")
            terminal.write(bytes(payload))

            self.assertEqual(terminal.scrollback_state()[0], 8)
            self.assertEqual(len(terminal.all_text()), 11)

    def test_one_line_history_limit_is_not_rounded_to_a_page(self):
        with Shitty(columns=8, rows=3, save_lines=1) as terminal:
            terminal.write(numbered_lines(0, 19))

            self.assertEqual(terminal.scrollback_state(), (1, 4, 3, 1))
            self.assertEqual(terminal.all_text(), ("016", "017", "018", "019"))

    def test_larger_history_limit_is_not_rounded_to_backing_capacity(self):
        with Shitty(columns=8, rows=3, save_lines=7) as terminal:
            terminal.write(numbered_lines(0, 39))

            self.assertEqual(terminal.scrollback_state(), (7, 10, 3, 7))
            self.assertEqual(terminal.all_text(), tuple(f"{n:03}" for n in range(30, 40)))

    def test_logical_line_limit_wins_with_large_auxiliary_payloads(self):
        with Shitty(columns=8, rows=3, save_lines=5) as terminal:
            payload = bytearray()
            for index in range(30):
                payload.extend(
                    f"\x1b[38;2;{index};{255 - index};{index * 3}m".encode()
                )
                payload.extend(b"\x1b]8;;https://example.test/" + b"y" * 512 + b"\x1b\\")
                payload.extend(f"{index:03}".encode() + b"\x1b]8;;\x1b\\\r\n")
            payload.extend(b"030")
            terminal.write(bytes(payload))

            self.assertEqual(terminal.scrollback_state()[0], 5)
            self.assertEqual(len(terminal.all_text()), 8)
            self.assertEqual(terminal.all_text()[-1], "030")

    def test_history_limit_remains_enforced_across_resize_and_sessions(self):
        with Shitty(columns=8, rows=4, save_lines=5) as terminal:
            terminal.write(numbered_lines(0, 19))
            terminal.resize(12, 2)
            self.assertLessEqual(terminal.scrollback_state()[0], 5)
            self.assertLessEqual(len(terminal.all_text()), 7)
            terminal.resize(6, 6)
            self.assertLessEqual(terminal.scrollback_state()[0], 5)

        with Shitty(columns=6, rows=2, save_lines=5) as second:
            second.write(numbered_lines(0, 19))
            self.assertEqual(second.scrollback_state()[0], 5)

    def test_pruning_an_anchored_oldest_row_clamps_viewport_to_new_top(self):
        with Shitty(columns=8, rows=3, save_lines=4) as terminal:
            terminal.write(numbered_lines(0, 6))
            terminal.wheel_up(4)
            self.assertEqual(visible_lines(terminal), ("000", "001", "002"))

            terminal.write(b"\r\n007")

            self.assertEqual(visible_lines(terminal), ("001", "002", "003"))
            self.assertEqual(terminal.scrollback_state(), (4, 7, 3, 0))

    def test_pruning_before_a_retained_anchor_preserves_its_contents(self):
        with Shitty(columns=8, rows=3, save_lines=6) as terminal:
            terminal.write(numbered_lines(0, 8))
            terminal.wheel_up(3)
            self.assertEqual(visible_lines(terminal), ("003", "004", "005"))

            terminal.write(b"\r\n009")

            self.assertEqual(visible_lines(terminal), ("003", "004", "005"))
            self.assertEqual(terminal.scrollback_state(), (6, 9, 3, 2))

    def test_erasing_history_invalidates_scrolled_viewport_geometry(self):
        with Shitty(columns=8, rows=3, save_lines=10) as terminal:
            terminal.write(numbered_lines(0, 8))
            terminal.wheel_up(3)
            self.assertEqual(visible_lines(terminal), ("003", "004", "005"))

            terminal.write(b"\x1b[3J")

            self.assertEqual(visible_lines(terminal), ("006", "007", "008"))
            self.assertEqual(terminal.snapshot().view_offset, 0)
            self.assertEqual(terminal.scrollback_state(), (0, 3, 3, 0))

    def test_single_row_prune_updates_retained_anchor_offset(self):
        with Shitty(columns=8, rows=3, save_lines=4) as terminal:
            terminal.write(numbered_lines(0, 6))
            terminal.wheel_up(2)
            self.assertEqual(visible_lines(terminal), ("002", "003", "004"))
            self.assertEqual(terminal.scrollback_state()[3], 2)

            terminal.write(b"\r\n007")

            self.assertEqual(visible_lines(terminal), ("002", "003", "004"))
            self.assertEqual(terminal.scrollback_state(), (4, 7, 3, 1))


if __name__ == "__main__":
    unittest.main()
