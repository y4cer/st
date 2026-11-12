# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


UPSTREAM_CASES = (
    "Screen: resize less cols with reflow previously wrapped",
    "Screen: resize less cols with reflow and scrollback",
    "Screen: resize less cols with reflow previously wrapped and scrollback",
    "Screen: resize less cols with scrollback keeps cursor row",
    "Screen: resize more rows, less cols with reflow with scrollback",
    "Screen: resize more rows then shrink again",
    "Screen: resize less cols to eliminate wide char",
    "Screen: resize less cols to wrap wide char",
    "Screen: resize less cols to eliminate wide char with row space",
    "Screen: resize less cols reflows cursor after wrapped text",
    "Screen: resize less cols reflows cursor after empty cells",
    "Screen: resize more cols with wide spacer head",
    "Screen: resize more cols with wide spacer head multiple lines",
    "Screen: resize more cols requiring a wide spacer head",
    "Screen: resize more cols with cursor at prompt",
    "Screen: resize more cols with cursor not at prompt",
    "Screen: resize with prompt_redraw last clears only one line",
    "Screen: resize with prompt_redraw last multiline prompt clears only last line",
    "Screen: select untracked",
    "Screen: select replaces existing pins",
)


def osc133(action):
    return b"\x1b]133;" + action + b"\x1b\\"


def visible_lines(terminal):
    return tuple(line.rstrip() for line in terminal.snapshot().lines)


def nonempty_visible_lines(terminal):
    lines = list(visible_lines(terminal))
    while lines and not lines[-1]:
        lines.pop()
    return tuple(lines)


class GhosttyScreenResizeWidePromptTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 20)
        self.assertEqual(len(set(UPSTREAM_CASES)), 20)

    def test_width_shrink_reflows_already_wrapped_rows(self):
        with Shitty(columns=5, rows=3, save_lines=0) as terminal:
            terminal.write(b"3IJKL4ABCD5EFGH")
            terminal.resize(3, 3)

            self.assertEqual(visible_lines(terminal), ("ABC", "D5E", "FGH"))

    def test_width_shrink_keeps_hard_lines_and_cursor_in_scrollback(self):
        with Shitty(columns=5, rows=3, save_lines=5) as terminal:
            terminal.write(b"1A\r\n2B\r\n3C\r\n4D\r\n5E\x1b[3;2H")
            terminal.resize(3, 3)
            snapshot = terminal.snapshot()

            self.assertEqual(visible_lines(terminal), ("3C", "4D", "5E"))
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 2))
            self.assertEqual(snapshot.cell(1, 2).char, "E")

    def test_width_shrink_reflows_wrapped_scrollback_and_cursor(self):
        with Shitty(columns=5, rows=3, save_lines=20) as terminal:
            terminal.write(b"1ABCD2EFGH3IJKL4ABCD5EFGH\x1b[3;5H")
            terminal.resize(3, 3)
            snapshot = terminal.snapshot()

            self.assertEqual(visible_lines(terminal), ("CD5", "EFG", "H"))
            self.assertEqual(
                terminal.all_text(),
                ("1AB", "CD2", "EFG", "H3I", "JKL", "4AB", "CD5", "EFG", "H"),
            )
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 2))
            self.assertEqual(snapshot.cell(0, 2).char, "H")

    @unittest.expectedFailure
    def test_width_shrink_keeps_the_cursor_row_on_a_scroll_cleared_page(self):
        with Shitty(columns=5, rows=3, save_lines=5) as terminal:
            terminal.write(b"1A\r\n2B\r\n3C\r\n4D\r\n5E")
            terminal.write(b"\x1b[22J\x1b[H")
            terminal.resize(3, 3)
            snapshot = terminal.snapshot()

            self.assertEqual(nonempty_visible_lines(terminal), ())
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 0))

    def test_unsupported_scroll_clear_does_not_corrupt_resize_or_cursor(self):
        with Shitty(columns=5, rows=3, save_lines=5) as terminal:
            terminal.write(b"1A\r\n2B\r\n3C\r\n4D\r\n5E")
            terminal.write(b"\x1b[22J\x1b[H")
            terminal.resize(3, 3)
            snapshot = terminal.snapshot()

            self.assertEqual(visible_lines(terminal), ("3C", "4D", "5E"))
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 0))

    def test_growing_rows_while_shrinking_columns_reflows_history(self):
        with Shitty(columns=5, rows=3, save_lines=20) as terminal:
            terminal.write(b"1ABCD\r\n2EFGH3IJKL\r\n4MNOP")
            terminal.resize(2, 10)

            self.assertEqual(
                visible_lines(terminal),
                ("BC", "D", "2E", "FG", "H3", "IJ", "KL", "4M", "NO", "P"),
            )
            self.assertEqual(
                terminal.all_text(),
                ("1A", "BC", "D", "2E", "FG", "H3", "IJ", "KL", "4M", "NO", "P"),
            )

    def test_grow_shrink_grow_round_trip_preserves_short_content(self):
        with Shitty(columns=5, rows=3, save_lines=10) as terminal:
            terminal.write(b"1ABC")
            for rows in (10, 3, 10):
                terminal.resize(5, rows)
                self.assertEqual(nonempty_visible_lines(terminal), ("1ABC",))
                self.assertEqual(terminal.all_text()[0], "1ABC")

    def test_one_column_resize_eliminates_an_unrepresentable_wide_char(self):
        with Shitty(columns=2, rows=1, save_lines=0) as terminal:
            terminal.write("😀".encode())
            terminal.resize(1, 1)
            snapshot = terminal.snapshot()

            self.assertEqual(visible_lines(terminal), ("",))
            self.assertFalse(snapshot.cell(0, 0).double_width)
            self.assertFalse(snapshot.cell(0, 0).double_width_continuation)

    def test_width_shrink_wraps_a_wide_char_as_one_grapheme(self):
        with Shitty(columns=3, rows=3, save_lines=0) as terminal:
            terminal.write("x😀".encode())
            terminal.resize(2, 3)
            snapshot = terminal.snapshot()

            self.assertEqual(visible_lines(terminal), ("x", "😀", ""))
            self.assertTrue(snapshot.cell(0, 0).wrapped)
            self.assertTrue(snapshot.cell(0, 1).double_width)
            self.assertTrue(snapshot.cell(1, 1).double_width_continuation)

    def test_extra_row_cannot_make_a_wide_char_fit_one_column(self):
        with Shitty(columns=2, rows=2, save_lines=0) as terminal:
            terminal.write("😀".encode())
            terminal.resize(1, 2)

            self.assertEqual(visible_lines(terminal), ("", ""))

    def test_width_shrink_reflows_cursor_after_written_text(self):
        with Shitty(columns=50, rows=7, save_lines=0) as terminal:
            terminal.write(b"a" * 30)
            terminal.resize(25, 7)
            snapshot = terminal.snapshot()

            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (5, 1))

    def test_width_shrink_reflows_cursor_across_unwritten_cells(self):
        with Shitty(columns=10, rows=3, save_lines=0) as terminal:
            terminal.write(b"abc\x1b[10G")
            terminal.resize(5, 3)
            snapshot = terminal.snapshot()

            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (4, 1))

    def test_width_growth_removes_a_wide_wrap_spacer(self):
        with Shitty(columns=3, rows=2, save_lines=0) as terminal:
            terminal.write("  😀".encode())
            terminal.resize(4, 2)
            snapshot = terminal.snapshot()

            self.assertEqual(nonempty_visible_lines(terminal), ("  😀",))
            self.assertTrue(snapshot.cell(2, 0).double_width)
            self.assertTrue(snapshot.cell(3, 0).double_width_continuation)

    def test_width_growth_removes_a_wide_wrap_spacer_across_rows(self):
        with Shitty(columns=3, rows=3, save_lines=0) as terminal:
            terminal.write("xxxyy😀".encode())
            terminal.resize(8, 2)
            snapshot = terminal.snapshot()

            self.assertEqual(nonempty_visible_lines(terminal), ("xxxyy😀",))
            self.assertTrue(snapshot.cell(5, 0).double_width)
            self.assertTrue(snapshot.cell(6, 0).double_width_continuation)

    def test_width_growth_keeps_a_required_wide_wrap_spacer(self):
        with Shitty(columns=2, rows=2, save_lines=0) as terminal:
            terminal.write("xx😀".encode())
            terminal.resize(3, 2)
            snapshot = terminal.snapshot()

            self.assertEqual(visible_lines(terminal), ("xx", "😀"))
            self.assertTrue(snapshot.cell(1, 0).wrapped)
            self.assertTrue(snapshot.cell(0, 1).double_width)
            self.assertTrue(snapshot.cell(1, 1).double_width_continuation)

    @unittest.expectedFailure
    def test_prompt_redraw_resize_clears_the_active_prompt(self):
        with Shitty(columns=10, rows=3, save_lines=5) as terminal:
            terminal.write(
                b"ABCDE\r\n" + osc133(b"P") + b"> " + osc133(b"B") + b"echo"
            )
            terminal.resize(20, 3)
            snapshot = terminal.snapshot()

            self.assertEqual(nonempty_visible_lines(terminal), ("ABCDE",))
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (6, 1))

    def test_prompt_redraw_resize_does_not_clear_completed_output(self):
        with Shitty(columns=10, rows=3, save_lines=5) as terminal:
            terminal.write(
                b"ABCDE\r\n"
                + osc133(b"P")
                + b"> "
                + osc133(b"B")
                + b"echo"
                + osc133(b"C")
                + b"\r\noutput"
            )
            terminal.resize(20, 3)
            snapshot = terminal.snapshot()

            self.assertEqual(
                nonempty_visible_lines(terminal),
                ("ABCDE", "> echo", "output"),
            )
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (6, 2))

    @unittest.expectedFailure
    def test_prompt_redraw_last_clears_only_the_current_input_line(self):
        with Shitty(columns=10, rows=4, save_lines=5) as terminal:
            terminal.write(
                b"ABCDE\r\n"
                + osc133(b"P")
                + b"> "
                + osc133(b"B")
                + b"hello\r\nworld"
            )
            terminal.resize(20, 4)

            self.assertEqual(nonempty_visible_lines(terminal), ("ABCDE", "> hello"))

    @unittest.expectedFailure
    def test_prompt_redraw_last_clears_only_the_last_prompt_line(self):
        with Shitty(columns=20, rows=5, save_lines=5) as terminal:
            terminal.write(
                osc133(b"P")
                + b"line1\r\n"
                + osc133(b"P;k=c")
                + b"line2\r\n"
                + osc133(b"P;k=c")
                + b"line3"
            )
            terminal.resize(30, 5)

            self.assertEqual(nonempty_visible_lines(terminal), ("line1", "line2"))

    def test_plain_resize_preserves_unsubmitted_prompt_rows(self):
        cases = (
            (10, 3, b"ABCDE\r\n" + osc133(b"P") + b"> " + osc133(b"B") + b"echo"),
            (10, 4, b"ABCDE\r\n" + osc133(b"P") + b"> " + osc133(b"B") + b"hello\r\nworld"),
            (20, 5, osc133(b"P") + b"line1\r\n" + osc133(b"P;k=c") + b"line2\r\n" + osc133(b"P;k=c") + b"line3"),
        )
        for columns, rows, data in cases:
            with self.subTest(columns=columns, rows=rows):
                with Shitty(columns=columns, rows=rows, save_lines=5) as terminal:
                    terminal.write(data)
                    before = nonempty_visible_lines(terminal)
                    terminal.resize(columns + 10, rows)
                    self.assertEqual(nonempty_visible_lines(terminal), before)

    def test_clearing_a_selection_releases_its_public_extent(self):
        with Shitty(columns=10, rows=3, save_lines=0) as terminal:
            terminal.write(b"ABC  DEF\r\n 123\r\n456")
            terminal.select_start(0, 0)
            terminal.select_update(3, 0)
            self.assertTrue(terminal.has_selection())
            terminal.select_clear()
            self.assertFalse(terminal.has_selection())

            terminal.select_start(0, 2)
            terminal.select_update(3, 2)
            self.assertEqual(terminal.select_finish(), b"456")

    def test_replacing_a_selection_drops_the_old_public_extent(self):
        with Shitty(columns=10, rows=3, save_lines=0) as terminal:
            terminal.write(b"ABC  DEF\r\n 123\r\n456")
            terminal.select_start(0, 0)
            terminal.select_update(3, 0)
            first = terminal.selection_state()

            terminal.select_start(0, 1)
            terminal.select_update(3, 1)
            second = terminal.selection_state()

            self.assertNotEqual(second, first)
            self.assertEqual(second["raw"], (0, 1, 3, 1))
            self.assertEqual(terminal.select_finish(), b" 12")


if __name__ == "__main__":
    unittest.main()
