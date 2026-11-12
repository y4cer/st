# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Public adaptations of xterm.js InputHandler cases 101 through 120."""

import unittest

from harness import Shitty


UPSTREAM_CASES = (
    "ICH deletes the final cell after pending wrap",
    "DECSTBM defaults to the whole viewport",
    "DECSTBM clamps its bottom margin",
    "DECSTBM applies only when top is above bottom",
    "DECSTBM homes the cursor",
    "scrollUp within margins",
    "scrollDown within margins",
    "insertLines outside margins",
    "insertLines within margins",
    "deleteLines outside margins",
    "deleteLines within margins",
    "large input is parsed in bounded subchunks",
    "window operations are disabled by default",
    "window operation 14 without a renderer",
    "window operation 16 without a renderer",
    "window operation 18 reports character dimensions",
    "default title stack selector",
    "icon title stack selector",
    "window title stack selector",
    "DECCOLM requires SetWinLines permission",
)


INITIAL_ROWS = b"0\r\n1\r\n2\r\n3\r\n4\r\n5\r\n6\r\n7\r\n8\r\n9"


def trimmed_lines(terminal):
    return [line.rstrip() for line in terminal.snapshot().lines]


def request_margins(terminal):
    terminal.write(b"\x1bP$qr\x1b\\")
    return terminal.read_input()


def window_terminal():
    return Shitty(
        columns=10,
        rows=10,
        extra_arguments=("-allowWindowOps", "true"),
    )


def title_queries():
    return b"\x1b[20t\x1b[21t"


def title_reports(icon, window):
    return b"\x1b]L" + icon + b"\x1b\\\x1b]l" + window + b"\x1b\\"


class XtermJsInputHandlerMarginsTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 20)
        self.assertEqual(len(set(UPSTREAM_CASES)), 20)

    def test_ich_deletes_the_final_cell_after_pending_wrap(self):
        with Shitty(columns=10, rows=10) as terminal:
            terminal.write(b"0123456789\x1b[@")
            self.assertEqual(terminal.snapshot().lines[0], "012345678 ")

    def test_decstbm_default_and_zero_margins_cover_the_viewport(self):
        with Shitty(columns=10, rows=10) as terminal:
            terminal.write(b"\x1b[r")
            self.assertEqual(request_margins(terminal), b"\x1bP1$r1;10r\x1b\\")
            terminal.write(b"\x1b[3;7r")
            self.assertEqual(request_margins(terminal), b"\x1bP1$r3;7r\x1b\\")
            terminal.write(b"\x1b[0;0r")
            self.assertEqual(request_margins(terminal), b"\x1bP1$r1;10r\x1b\\")

    def test_decstbm_clamps_bottom_to_the_viewport(self):
        with Shitty(columns=10, rows=10) as terminal:
            terminal.write(b"\x1b[3;1000r")
            self.assertEqual(request_margins(terminal), b"\x1bP1$r3;10r\x1b\\")

    def test_decstbm_rejects_top_at_or_below_bottom(self):
        with Shitty(columns=10, rows=10) as terminal:
            terminal.write(b"\x1b[7;2r")
            self.assertEqual(request_margins(terminal), b"\x1bP1$r1;10r\x1b\\")

    def test_decstbm_homes_cursor(self):
        with Shitty(columns=10, rows=10) as terminal:
            terminal.write(b"\x1b[10;10H\x1b[2;7r")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 0))

    def test_scroll_up_is_limited_to_vertical_margins(self):
        with Shitty(columns=10, rows=10) as terminal:
            terminal.write(INITIAL_ROWS + b"\x1b[2;4r\x1b[2Sm")
            self.assertEqual(
                trimmed_lines(terminal),
                ["m", "3", "", "", "4", "5", "6", "7", "8", "9"],
            )

    def test_scroll_down_is_limited_to_vertical_margins(self):
        with Shitty(columns=10, rows=10) as terminal:
            terminal.write(INITIAL_ROWS + b"\x1b[2;4r\x1b[2Tm")
            self.assertEqual(
                trimmed_lines(terminal),
                ["m", "", "", "1", "4", "5", "6", "7", "8", "9"],
            )

    def test_insert_lines_is_ignored_outside_vertical_margins(self):
        with Shitty(columns=10, rows=10) as terminal:
            terminal.write(INITIAL_ROWS + b"\x1b[3;6r\x1b[2Lm")
            self.assertEqual(trimmed_lines(terminal), ["m", "1", "2", "3", "4", "5", "6", "7", "8", "9"])
            terminal.write(b"\x1b[2H\x1b[2Ln")
            self.assertEqual(trimmed_lines(terminal), ["m", "n", "2", "3", "4", "5", "6", "7", "8", "9"])
            terminal.write(b"\x1b[7H\x1b[2Lo\x1b[8H\x1b[2Lp\x1b[100H\x1b[2Lq")
            self.assertEqual(trimmed_lines(terminal), ["m", "n", "2", "3", "4", "5", "o", "p", "8", "q"])

    def test_insert_lines_shifts_only_rows_within_vertical_margins(self):
        with Shitty(columns=10, rows=10) as terminal:
            terminal.write(INITIAL_ROWS + b"\x1b[3;6r\x1b[3H\x1b[2Lm")
            self.assertEqual(trimmed_lines(terminal), ["0", "1", "m", "", "2", "3", "6", "7", "8", "9"])
            terminal.write(b"\x1b[6H\x1b[2Ln")
            self.assertEqual(trimmed_lines(terminal), ["0", "1", "m", "", "2", "n", "6", "7", "8", "9"])

    def test_delete_lines_is_ignored_outside_vertical_margins(self):
        with Shitty(columns=10, rows=10) as terminal:
            terminal.write(INITIAL_ROWS + b"\x1b[3;6r\x1b[2Mm")
            self.assertEqual(trimmed_lines(terminal), ["m", "1", "2", "3", "4", "5", "6", "7", "8", "9"])
            terminal.write(b"\x1b[2H\x1b[2Mn")
            self.assertEqual(trimmed_lines(terminal), ["m", "n", "2", "3", "4", "5", "6", "7", "8", "9"])
            terminal.write(b"\x1b[7H\x1b[2Mo\x1b[8H\x1b[2Mp\x1b[100H\x1b[2Mq")
            self.assertEqual(trimmed_lines(terminal), ["m", "n", "2", "3", "4", "5", "o", "p", "8", "q"])

    def test_delete_lines_shifts_only_rows_within_vertical_margins(self):
        with Shitty(columns=10, rows=10) as terminal:
            terminal.write(INITIAL_ROWS + b"\x1b[3;6r\x1b[6H\x1b[2Mm")
            self.assertEqual(trimmed_lines(terminal), ["0", "1", "2", "3", "4", "m", "6", "7", "8", "9"])
            terminal.write(b"\x1b[3H\x1b[2Mn")
            self.assertEqual(trimmed_lines(terminal), ["0", "1", "n", "m", "", "", "6", "7", "8", "9"])

    def test_large_input_reaches_public_terminal_state_past_every_subchunk(self):
        with Shitty(columns=10, rows=10) as terminal:
            terminal.write(b"12345")
            terminal.write(b"a" * 10000)
            terminal.write(b"a" * 200000)
            terminal.write(b"a" * 300000 + b"\x1b[2J\x1b[Hdone")
            self.assertEqual(terminal.snapshot().lines[0], "done      ")

    def test_window_operations_are_silent_by_default(self):
        with Shitty(columns=10, rows=10) as terminal:
            terminal.write(b"\x1b[14t\x1b[16t\x1b[18t\x1b[20t\x1b[21t")
            self.assertEqual(terminal.read_input(), b"")

    @unittest.expectedFailure
    def test_pixel_size_query_is_silent_without_xtermjs_renderer(self):
        with window_terminal() as terminal:
            terminal.write(b"\x1b[14t")
            self.assertEqual(terminal.read_input(), b"")

    @unittest.expectedFailure
    def test_cell_size_query_is_silent_without_xtermjs_renderer(self):
        with window_terminal() as terminal:
            terminal.write(b"\x1b[16t")
            self.assertEqual(terminal.read_input(), b"")

    def test_character_size_query_reports_current_grid(self):
        with window_terminal() as terminal:
            terminal.write(b"\x1b[18t")
            self.assertEqual(terminal.read_input(), b"\x1b[8;10;10t")
            terminal.resize(50, 20)
            terminal.write(b"\x1b[18t")
            self.assertEqual(terminal.read_input(), b"\x1b[8;20;50t")

    def test_default_title_stack_selector_restores_both_titles(self):
        with window_terminal() as terminal:
            terminal.write(
                b"\x1b]0;1\x07\x1b[22t"
                b"\x1b]0;2\x07\x1b[22t"
                b"\x1b]0;3\x07\x1b[22t"
            )
            for expected in (b"3", b"2", b"1", b"1"):
                terminal.write(b"\x1b[23t" + title_queries())
                self.assertEqual(terminal.read_input(), title_reports(expected, expected))

    def test_icon_title_stack_selector_restores_only_icon_title(self):
        with window_terminal() as terminal:
            terminal.write(
                b"\x1b]0;1\x07\x1b[22;1t"
                b"\x1b]0;2\x07\x1b[22;1t"
                b"\x1b]0;3\x07\x1b[22;1t"
            )
            for expected_icon in (b"3", b"2", b"1", b"1"):
                terminal.write(b"\x1b[23;1t" + title_queries())
                self.assertEqual(terminal.read_input(), title_reports(expected_icon, b"3"))

    def test_window_title_stack_selector_restores_only_window_title(self):
        with window_terminal() as terminal:
            terminal.write(
                b"\x1b]0;1\x07\x1b[22;2t"
                b"\x1b]0;2\x07\x1b[22;2t"
                b"\x1b]0;3\x07\x1b[22;2t"
            )
            for expected_window in (b"3", b"2", b"1", b"1"):
                terminal.write(b"\x1b[23;2t" + title_queries())
                self.assertEqual(terminal.read_input(), title_reports(b"3", expected_window))

    def test_deccolm_requires_column_mode_permission(self):
        with window_terminal() as terminal:
            terminal.write(b"\x1b[?40l\x1b[?3l\x1b[?3h")
            self.assertEqual(terminal.snapshot().columns, 10)
            terminal.write(b"\x1b[?40h\x1b[?3l")
            self.assertEqual(terminal.snapshot().columns, 80)
            terminal.write(b"\x1b[?3h")
            self.assertEqual(terminal.snapshot().columns, 132)


if __name__ == "__main__":
    unittest.main()
