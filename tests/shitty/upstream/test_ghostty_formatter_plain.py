# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty, put_rows


UPSTREAM_CASES = (
    "Page plain single line",
    "Page plain single line soft-wrapped unwrapped",
    "Page plain single wide char",
    "Page plain single wide char soft-wrapped unwrapped",
    "Page plain multiline",
    "Page plain multiline rectangle",
    "Page plain multi blank lines",
    "Page plain trailing blank lines",
    "Page plain trailing whitespace",
    "Page plain trailing whitespace no trim",
    "Page plain with prior trailing state rows",
    "Page plain with prior trailing state cells no wrapped line",
    "Page plain with prior trailing state cells with wrap continuation",
    "Page plain soft-wrapped without unwrap",
    "Page plain soft-wrapped with unwrap",
    "Page plain soft-wrapped 3 lines without unwrap",
    "Page plain soft-wrapped 3 lines with unwrap",
    "Page plain start_y subset",
    "Page plain end_y subset",
    "Page plain start_y and end_y range",
)


def select(terminal, start, end, rectangular=False):
    terminal.select_start(*start)
    if rectangular:
        terminal.select_rectangular()
    terminal.select_update(*end)
    return terminal.select_finish()


class GhosttyFormatterPlainTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 20)
        self.assertEqual(len(set(UPSTREAM_CASES)), 20)

    def test_plain_single_line_copies_only_written_text(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"hello, world")

            self.assertEqual(select(terminal, (0, 0), (80, 0)), b"hello, world")

    def test_copy_unwraps_one_soft_wrapped_line(self):
        with Shitty(columns=3, rows=5, save_lines=0) as terminal:
            terminal.write(b"hello!")

            self.assertEqual(select(terminal, (0, 0), (3, 1)), b"hello!")

    def test_wide_cell_selection_expands_from_either_half(self):
        text = "1A⚡".encode()
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(text)

            self.assertEqual(select(terminal, (0, 0), (4, 0)), text)
            self.assertEqual(select(terminal, (2, 0), (4, 0)), "⚡".encode())
            self.assertEqual(select(terminal, (3, 0), (4, 0)), "⚡".encode())

    def test_wide_cell_selection_unwraps_a_right_edge_spacer(self):
        text = "1A⚡".encode()
        with Shitty(columns=3, rows=3, save_lines=0) as terminal:
            terminal.write(text)

            self.assertEqual(select(terminal, (0, 0), (2, 1)), text)
            self.assertEqual(select(terminal, (0, 1), (2, 1)), "⚡".encode())
            self.assertEqual(select(terminal, (1, 1), (2, 1)), "⚡".encode())

    def test_plain_multiline_copy_uses_line_feed_separators(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"hello\r\nworld")

            self.assertEqual(select(terminal, (0, 0), (5, 1)), b"hello\nworld")

    def test_rectangular_copy_applies_the_same_columns_to_each_row(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"hello\r\nworld")

            self.assertEqual(select(terminal, (1, 0), (4, 1), rectangular=True), b"ell\norl")

    def test_plain_copy_preserves_blank_rows_between_content(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"hello\r\n\r\n\r\nworld")

            self.assertEqual(select(terminal, (0, 0), (5, 3)), b"hello\n\n\nworld")

    def test_plain_copy_trims_trailing_blank_rows(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"hello\r\nworld\r\n\r\n")

            self.assertEqual(select(terminal, (0, 0), (80, 23)), b"hello\nworld")

    @unittest.expectedFailure
    def test_plain_copy_trims_trailing_spaces_when_it_consumes_whole_rows(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"hello   \r\nworld   ")

            self.assertEqual(select(terminal, (0, 0), (80, 23)), b"hello\nworld")

    def test_explicit_single_row_range_preserves_selected_trailing_spaces(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"hello   ")

            self.assertEqual(select(terminal, (0, 0), (8, 0)), b"hello   ")

    def test_blank_rows_before_content_survive_cross_page_formatting_state(self):
        with Shitty(columns=80, rows=300, save_lines=0) as terminal:
            terminal.write(put_rows(b"", b"", b"hello"))

            self.assertEqual(select(terminal, (0, 0), (5, 2)), b"\n\nhello")

    def test_hard_row_boundary_resets_prior_trailing_cell_state(self):
        with Shitty(columns=80, rows=300, save_lines=0) as terminal:
            terminal.write(put_rows(b"abc", b"hello"))

            self.assertEqual(select(terminal, (0, 0), (5, 1)), b"abc\nhello")

    def test_soft_continuation_uses_prior_trailing_cells_without_a_newline(self):
        with Shitty(columns=3, rows=300, save_lines=0) as terminal:
            terminal.write(b"abcworld")

            self.assertEqual(select(terminal, (0, 0), (2, 2)), b"abcworld")

    def test_physical_plain_rows_keep_a_two_line_soft_wrap(self):
        with Shitty(columns=10, rows=24, save_lines=0) as terminal:
            terminal.write(b"hello world test")

            self.assertEqual(terminal.all_text()[:2], ("hello worl", "d test"))

    def test_copy_joins_a_two_line_soft_wrap(self):
        with Shitty(columns=10, rows=24, save_lines=0) as terminal:
            terminal.write(b"hello world test")

            self.assertEqual(select(terminal, (0, 0), (6, 1)), b"hello world test")

    @unittest.expectedFailure
    def test_physical_plain_rows_keep_a_three_line_soft_wrap(self):
        with Shitty(columns=10, rows=24, save_lines=0) as terminal:
            terminal.write(b"hello world this is a test")

            self.assertEqual(terminal.all_text()[:3], ("hello worl", "d this is", "a test"))

    def test_copy_joins_a_three_line_soft_wrap(self):
        text = b"hello world this is a test"
        with Shitty(columns=10, rows=24, save_lines=0) as terminal:
            terminal.write(text)

            self.assertEqual(select(terminal, (0, 0), (6, 2)), text)

    def test_plain_range_can_start_at_a_later_row(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"hello\r\nworld\r\ntest")

            self.assertEqual(select(terminal, (0, 1), (4, 2)), b"world\ntest")

    def test_plain_range_can_end_at_an_earlier_row(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"hello\r\nworld\r\ntest")

            self.assertEqual(select(terminal, (0, 0), (5, 1)), b"hello\nworld")

    def test_plain_range_can_select_only_middle_rows(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"hello\r\nworld\r\ntest\r\nfoo")

            self.assertEqual(select(terminal, (0, 1), (4, 2)), b"world\ntest")


if __name__ == "__main__":
    unittest.main()
