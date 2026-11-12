# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Public adaptations of xterm.js SelectionService cases 1 through 19."""

import unittest

from harness import Shitty, put_rows


UPSTREAM_CASES = (
    "word selection expands normal-width characters",
    "word selection expands whitespace",
    "word selection handles wide characters",
    "word selection trims commonly adjacent path punctuation",
    "word selection expands across one soft wrap",
    "word selection expands across many soft wraps",
    "one emoji surrounded by spaces is one word",
    "multiple emoji surrounded by spaces are one word",
    "ZWJ emoji components form one word",
    "emoji and ordinary characters joined together form one word",
    "complex emoji and ordinary characters joined together form one word",
    "line selection selects an entire physical line",
    "line selection selects an entire soft-wrapped line",
    "select all reaches beyond the viewport",
    "select lines selects one line",
    "select lines selects multiple lines",
    "select lines clamps a negative first row",
    "select lines clamps a final row beyond the buffer",
    "hasSelection reports empty and non-empty ranges",
)


def select_word(terminal, column, row=0):
    terminal.select_start(column, row)
    terminal.select_extend(column, row, cycle=True)
    return terminal.select_finish()


def select_line(terminal, column, row=0):
    terminal.select_start(column, row)
    terminal.select_extend(column, row, cycle=True)
    terminal.select_extend(column, row, cycle=True)
    return terminal.select_finish()


def select_lines(terminal, start_row, end_row):
    terminal.select_start(0, start_row)
    terminal.select_extend(0, start_row, cycle=True)
    terminal.select_extend(0, start_row, cycle=True)
    terminal.select_update(terminal.snapshot().columns, end_row)
    return terminal.select_finish()


class XtermJsSelectionServiceTest(unittest.TestCase):
    def test_upstream_inventory_has_19_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 19)
        self.assertEqual(len(set(UPSTREAM_CASES)), 19)

    def test_word_selection_expands_normal_width_characters(self):
        with Shitty(columns=20, rows=2) as terminal:
            terminal.write(b"foo bar")
            expected = (b"foo", b"foo", b"foo", b" ", b"bar", b"bar", b"bar")
            self.assertEqual(
                tuple(select_word(terminal, column) for column in range(7)),
                expected,
            )

    def test_word_selection_expands_whitespace(self):
        with Shitty(columns=20, rows=2) as terminal:
            terminal.write(b"a   b")
            self.assertEqual(
                tuple(select_word(terminal, column) for column in range(5)),
                (b"a", b"   ", b"   ", b"   ", b"b"),
            )

    def test_word_selection_handles_wide_characters(self):
        with Shitty(columns=20, rows=2) as terminal:
            terminal.write("中文 a中文b foo".encode())
            expected = {
                0: "中文",
                1: "中文",
                2: "中文",
                3: "中文",
                4: " ",
                5: "a中文b",
                6: "a中文b",
                7: "a中文b",
                8: "a中文b",
                9: "a中文b",
                10: "a中文b",
                11: " ",
                12: "foo",
                13: "foo",
                14: "foo",
            }
            self.assertEqual(
                {column: select_word(terminal, column).decode() for column in expected},
                expected,
            )

    @unittest.expectedFailure
    def test_word_selection_trims_adjacent_path_punctuation(self):
        with Shitty(columns=20, rows=2) as terminal:
            terminal.write(b"(cd)[ef]{gh}'ij\"")
            expected = (
                b"(cd", b"cd", b"cd", b"cd)",
                b"[ef", b"ef", b"ef", b"ef]",
                b"{gh", b"gh", b"gh", b"gh}",
                b"'ij", b"ij", b"ij", b'ij"',
            )
            self.assertEqual(
                tuple(select_word(terminal, column) for column in range(16)),
                expected,
            )

    def test_word_selection_expands_across_one_soft_wrap(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"                 foobar")
            self.assertEqual(select_word(terminal, 18, 0), b"foobar")
            self.assertEqual(select_word(terminal, 1, 1), b"foobar")

    def test_word_selection_expands_across_many_soft_wraps(self):
        text = b"foo" + b"a" * 20 + b"b" * 20 + b"c" * 20 + b"bar"
        with Shitty(columns=20, rows=6) as terminal:
            terminal.write(b" " * 17 + text)
            for column, row in ((18, 0), (10, 1), (10, 2), (10, 3), (1, 4)):
                with self.subTest(column=column, row=row):
                    self.assertEqual(select_word(terminal, column, row), text)

    def test_single_emoji_is_one_word(self):
        with Shitty(columns=20, rows=2) as terminal:
            terminal.write(" ⚽ a".encode())
            self.assertEqual(select_word(terminal, 0), b" ")
            self.assertEqual(select_word(terminal, 1), "⚽".encode())
            self.assertEqual(select_word(terminal, 3), b" ")

    def test_multiple_emoji_are_one_word(self):
        with Shitty(columns=20, rows=2) as terminal:
            terminal.write(" ⚽⚽ a".encode())
            self.assertEqual(select_word(terminal, 1), "⚽⚽".encode())
            self.assertEqual(select_word(terminal, 3), "⚽⚽".encode())

    def test_zwj_emoji_components_form_one_word(self):
        with Shitty(columns=20, rows=2) as terminal:
            terminal.write(" 👨‍👩‍👧‍👦 a".encode())
            self.assertEqual(select_word(terminal, 1), "👨‍👩‍👧‍👦".encode())
            self.assertEqual(select_word(terminal, 2), "👨‍👩‍👧‍👦".encode())

    @unittest.expectedFailure
    def test_emoji_and_characters_joined_form_one_word(self):
        with Shitty(columns=30, rows=2) as terminal:
            terminal.write(" ⚽ab cd⚽ ef⚽gh".encode())
            for column in (1, 3, 4):
                self.assertEqual(select_word(terminal, column), "⚽ab".encode())
            for column in (6, 8, 9):
                self.assertEqual(select_word(terminal, column), "cd⚽".encode())
            for column in (11, 13, 15):
                self.assertEqual(select_word(terminal, column), "ef⚽gh".encode())

    @unittest.expectedFailure
    def test_complex_emoji_and_characters_form_one_word(self):
        flag = "🏴󠁧󠁢󠁥󠁮󠁧󠁿"
        with Shitty(columns=30, rows=2) as terminal:
            terminal.write(f" {flag}ab cd{flag} ef{flag}gh a".encode())
            self.assertEqual(select_word(terminal, 1), f"{flag}ab".encode())
            self.assertEqual(select_word(terminal, 6), f"cd{flag}".encode())
            self.assertEqual(select_word(terminal, 12), f"ef{flag}gh".encode())

    def test_line_selection_selects_entire_physical_line(self):
        with Shitty(columns=20, rows=2) as terminal:
            terminal.write(b"foo bar")
            self.assertEqual(select_line(terminal, 2), b"foo bar")

    def test_line_selection_selects_entire_soft_wrapped_line(self):
        with Shitty(columns=3, rows=3) as terminal:
            terminal.write(b"foobar")
            self.assertEqual(select_line(terminal, 1, 0), b"foobar")
            self.assertEqual(select_line(terminal, 1, 1), b"foobar")

    def test_select_all_reaches_beyond_the_viewport(self):
        rows = (b"1", b"2", b"3", b"4", b"5", b"6", b"7", b"8")
        with Shitty(columns=20, rows=5, save_lines=10) as terminal:
            terminal.write(b"\r\n".join(rows))
            terminal.wheel_up(3)
            terminal.button(0, True, x=2, y=2)
            terminal.pointer(x=22, y=6)
            for _ in range(3):
                terminal.selection_autoscroll_tick()
            self.assertEqual(
                terminal.button(0, False, x=22, y=6),
                b"\n".join(rows),
            )

    def test_select_lines_selects_one_line(self):
        with Shitty(columns=20, rows=3, save_lines=0) as terminal:
            terminal.write(put_rows(b"1", b"2", b"3"))
            self.assertEqual(select_lines(terminal, 1, 1), b"2")

    def test_select_lines_selects_multiple_lines(self):
        with Shitty(columns=20, rows=5, save_lines=0) as terminal:
            terminal.write(put_rows(b"1", b"2", b"3", b"4", b"5"))
            self.assertEqual(select_lines(terminal, 1, 3), b"2\n3\n4")

    def test_select_lines_clamps_negative_first_row(self):
        with Shitty(columns=20, rows=2, save_lines=0) as terminal:
            terminal.write(put_rows(b"1", b"2"))
            self.assertEqual(select_lines(terminal, -1, 0), b"1")

    def test_select_lines_clamps_row_beyond_buffer(self):
        with Shitty(columns=20, rows=2, save_lines=0) as terminal:
            terminal.write(put_rows(b"1", b"2"))
            self.assertEqual(select_lines(terminal, 1, 2), b"2")

    def test_has_selection_reports_empty_and_nonempty_ranges(self):
        with Shitty(columns=20, rows=2) as terminal:
            terminal.select_start(0, 0)
            self.assertFalse(terminal.has_selection())
            terminal.select_update(0, 0)
            self.assertFalse(terminal.has_selection())
            terminal.select_update(1, 0)
            self.assertTrue(terminal.has_selection())
            terminal.select_clear()
            self.assertFalse(terminal.has_selection())


if __name__ == "__main__":
    unittest.main()
