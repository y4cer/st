# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


UPSTREAM_CASES = (
    "Screen: reselecting tracked selection preserves its pins",
    "Screen: promptClickMove line left skips non-input cells",
    "Screen: promptClickMove line left soft-wrapped line",
    "Screen: promptClickMove line left stops at hard wrap",
    "Screen: promptClickMove click right of input same line",
    "Screen: promptClickMove click right of input cursor at end",
    "Screen: promptClickMove click right of input on lower line",
    "Screen: promptClickMove click right of input cursor at end lower line",
    "Screen: promptClickMove click right of input cursor on last char",
)


def osc133(action, options=b""):
    suffix = b";" + options if options else b""
    return b"\x1b]133;" + action + suffix + b"\x1b\\"


def click_input(terminal, column, row, time=1.0):
    terminal.button(0, True, x=column + 2, y=row + 2, time=time)
    terminal.button(0, False, x=column + 2, y=row + 2, time=time + 0.01)
    return terminal.read_all_input()


def prompt_with_input(value=b"hello"):
    return (
        osc133(b"A", b"cl=line")
        + b"> "
        + osc133(b"B")
        + value
    )


class GhosttyScreenPromptClickTailTest(unittest.TestCase):
    def test_upstream_inventory_has_all_9_remaining_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 9)
        self.assertEqual(len(set(UPSTREAM_CASES)), 9)

    def test_reselecting_the_same_public_extent_preserves_its_order(self):
        with Shitty(columns=10, rows=2, save_lines=0) as terminal:
            terminal.write(b"ABCDE")
            terminal.select_start(1, 0)
            terminal.select_update(3, 0)
            first = terminal.selection_state()

            terminal.select_start(1, 0)
            terminal.select_update(3, 0)
            second = terminal.selection_state()

            self.assertEqual(second, first)
            self.assertEqual(second["raw"], (1, 0, 3, 0))
            self.assertEqual(terminal.select_finish(), b"BC")

    @unittest.expectedFailure
    def test_prompt_click_left_skips_non_input_cells(self):
        with Shitty(columns=20, rows=5) as terminal:
            terminal.write(
                osc133(b"A", b"cl=line")
                + b"> "
                + osc133(b"B")
                + b"h"
                + osc133(b"C")
                + b"X"
                + osc133(b"B")
                + b"llo"
                + b"\x1b[1;7H"
            )

            self.assertEqual(click_input(terminal, 2, 0), b"\x1b[D" * 3)

    @unittest.expectedFailure
    def test_prompt_click_left_counts_input_across_a_soft_wrap(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(prompt_with_input(b"abcdefghij") + b"\x1b[2;2H")

            self.assertEqual(click_input(terminal, 2, 0), b"\x1b[D" * 9)

    @unittest.expectedFailure
    def test_prompt_click_left_stops_at_a_hard_line_break(self):
        with Shitty(columns=20, rows=5) as terminal:
            terminal.write(prompt_with_input(b"hello\r\nworld") + b"\x1b[2;5H")

            self.assertEqual(click_input(terminal, 2, 0), b"\x1b[D" * 4)

    @unittest.expectedFailure
    def test_prompt_click_right_of_input_moves_to_its_end(self):
        with Shitty(columns=20, rows=5) as terminal:
            terminal.write(prompt_with_input() + b"\x1b[1;3H")

            self.assertEqual(click_input(terminal, 15, 0), b"\x1b[C" * 5)

    def test_prompt_click_right_needs_no_move_when_cursor_is_at_end(self):
        with Shitty(columns=20, rows=5) as terminal:
            terminal.write(prompt_with_input())

            self.assertEqual(click_input(terminal, 15, 0), b"")

    @unittest.expectedFailure
    def test_prompt_click_on_a_lower_line_moves_to_input_end(self):
        with Shitty(columns=20, rows=5) as terminal:
            terminal.write(prompt_with_input() + b"\x1b[1;3H")

            self.assertEqual(click_input(terminal, 5, 1), b"\x1b[C" * 5)

    def test_prompt_click_on_a_lower_line_is_idle_at_input_end(self):
        with Shitty(columns=20, rows=5) as terminal:
            terminal.write(prompt_with_input())

            self.assertEqual(click_input(terminal, 5, 1), b"")

    @unittest.expectedFailure
    def test_prompt_click_right_moves_once_from_the_last_input_char(self):
        with Shitty(columns=20, rows=5) as terminal:
            terminal.write(prompt_with_input() + b"\x1b[1;7H")

            self.assertEqual(click_input(terminal, 15, 0), b"\x1b[C")


if __name__ == "__main__":
    unittest.main()
