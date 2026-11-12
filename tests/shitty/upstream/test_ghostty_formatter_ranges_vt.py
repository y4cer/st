# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty, put_rows


UPSTREAM_CASES = (
    "Page plain start_y out of bounds",
    "Page plain end_y greater than rows",
    "Page plain end_y less than start_y",
    "Page plain start_x on first row only",
    "Page plain end_x on last row only",
    "Page plain start_x and end_x multiline",
    "Page plain start_x out of bounds",
    "Page plain end_x greater than cols",
    "Page plain end_x less than start_x single row",
    "Page plain start_y non-zero ignores trailing state",
    "Page plain start_x non-zero ignores trailing state",
    "Page plain start_y and start_x zero uses trailing state",
    "Page plain single line with styling",
    "Page VT single line plain text",
    "Page VT single line with bold",
    "Page VT multiple styles",
    "Page VT with foreground color",
    "Page VT with background and foreground colors",
    "Page VT multi-line with styles",
    "Page VT duplicate style not emitted twice",
)


def select(terminal, start, end):
    terminal.select_start(*start)
    terminal.select_update(*end)
    return terminal.select_finish()


class GhosttyFormatterRangesVtTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 20)
        self.assertEqual(len(set(UPSTREAM_CASES)), 20)

    def test_copy_started_below_the_page_clamps_to_an_empty_tail(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"hello")

            self.assertEqual(select(terminal, (0, 30), (80, 30)), b"")

    def test_copy_ending_below_the_page_includes_all_available_text(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"hello")

            self.assertEqual(select(terminal, (0, 0), (80, 30)), b"hello")

    def test_reversed_y_range_over_blank_rows_copies_no_text(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"hello")

            self.assertEqual(select(terminal, (80, 5), (0, 2)), b"")

    def test_copy_start_column_applies_only_to_the_first_row(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"hello world")

            self.assertEqual(select(terminal, (6, 0), (80, 23)), b"world")

    def test_copy_end_column_applies_only_to_the_last_row(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"first line\r\nsecond line\r\nthird line")

            self.assertEqual(
                select(terminal, (0, 0), (5, 2)),
                b"first line\nsecond line\nthird",
            )

    def test_copy_uses_partial_first_and_last_rows_with_full_middle_rows(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"hello world\r\ntest case\r\nfoo bar")

            self.assertEqual(
                select(terminal, (6, 0), (3, 2)),
                b"world\ntest case\nfoo",
            )

    def test_copy_start_column_beyond_the_page_clamps_to_empty(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"hello")

            self.assertEqual(select(terminal, (100, 0), (100, 0)), b"")

    def test_copy_end_column_beyond_the_page_clamps_after_written_text(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"hello")

            self.assertEqual(select(terminal, (0, 0), (100, 0)), b"hello")

    def test_reversed_x_range_is_normalized_without_copying_implicit_padding(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"hello")

            self.assertEqual(select(terminal, (10, 0), (5, 0)), b"")

    def test_copy_starting_on_a_later_row_ignores_prior_rows(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"hello\r\nworld")

            self.assertEqual(select(terminal, (0, 1), (80, 30)), b"world")

    def test_copy_starting_at_a_later_column_ignores_prior_cells(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"hello world")

            self.assertEqual(select(terminal, (6, 0), (80, 30)), b"world")

    def test_copy_from_the_origin_keeps_leading_blank_rows(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(put_rows(b"", b"", b"hello"))

            self.assertEqual(select(terminal, (0, 0), (5, 2)), b"\n\nhello")

    def test_plain_copy_removes_sgr_without_losing_cell_style(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"hello, \x1b[1mworld\x1b[0m")
            snapshot = terminal.snapshot()

            self.assertEqual(select(terminal, (0, 0), (12, 0)), b"hello, world")
            self.assertFalse(snapshot.cell(6, 0).bold)
            self.assertTrue(all(snapshot.cell(column, 0).bold for column in range(7, 12)))

    def test_plain_vt_replay_draws_only_plain_text(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"hello")
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.lines[0].rstrip(), "hello")
            self.assertTrue(all(not snapshot.cell(column, 0).bold for column in range(5)))

    def test_bold_vt_replay_scopes_the_style_to_its_text(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"\x1b[0m\x1b[1mhello\x1b[0mX")
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.lines[0].rstrip(), "helloX")
            self.assertTrue(all(snapshot.cell(column, 0).bold for column in range(5)))
            self.assertFalse(snapshot.cell(5, 0).bold)

    def test_multiple_style_vt_replay_preserves_each_style_run(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(
                b"\x1b[0m\x1b[1mhello "
                b"\x1b[0m\x1b[1m\x1b[3mworld\x1b[0m"
            )
            snapshot = terminal.snapshot()

            for column in range(6):
                self.assertTrue(snapshot.cell(column, 0).bold)
                self.assertFalse(snapshot.cell(column, 0).italic)
            for column in range(6, 11):
                self.assertTrue(snapshot.cell(column, 0).bold)
                self.assertTrue(snapshot.cell(column, 0).italic)

    def test_indexed_foreground_vt_replay_resolves_the_palette_color(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"\x1b[0m\x1b[38;5;1mred\x1b[0mX")
            snapshot = terminal.snapshot()

            for column in range(3):
                self.assertEqual(snapshot.cell(column, 0).foreground, (170, 0, 0))
            self.assertNotEqual(snapshot.cell(3, 0).foreground, (170, 0, 0))

    def test_dynamic_default_color_vt_replay_recolors_plain_text(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(
                b"\x1b]10;rgb:ab/cd/ef\x1b\\"
                b"\x1b]11;rgb:12/34/56\x1b\\hello"
            )
            snapshot = terminal.snapshot()

            for column in range(5):
                self.assertEqual(snapshot.cell(column, 0).foreground, (0xAB, 0xCD, 0xEF))
                self.assertEqual(snapshot.cell(column, 0).background, (0x12, 0x34, 0x56))

    def test_multiline_vt_replay_resets_style_at_the_hard_boundary(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(
                b"\x1b[0m\x1b[1mfirst\x1b[0m\r\n"
                b"\x1b[0m\x1b[3msecond\x1b[0m"
            )
            snapshot = terminal.snapshot()

            self.assertTrue(all(snapshot.cell(column, 0).bold for column in range(5)))
            self.assertTrue(all(not snapshot.cell(column, 0).italic for column in range(5)))
            self.assertTrue(all(snapshot.cell(column, 1).italic for column in range(6)))
            self.assertTrue(all(not snapshot.cell(column, 1).bold for column in range(6)))

    def test_duplicate_bold_vt_replay_does_not_split_the_style_run(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"\x1b[0m\x1b[1mhel\x1b[1mlo\x1b[0mX")
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.lines[0].rstrip(), "helloX")
            self.assertTrue(all(snapshot.cell(column, 0).bold for column in range(5)))
            self.assertFalse(snapshot.cell(5, 0).bold)


if __name__ == "__main__":
    unittest.main()
