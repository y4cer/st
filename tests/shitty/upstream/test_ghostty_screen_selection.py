# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty, put_rows


UPSTREAM_CASES = (
    "Screen: hyperlink start/end",
    "Screen: hyperlink accepts its current values",
    "Screen: hyperlink reuse",
    "Screen: selectLine",
    "Screen: selectLine across full soft-wrap",
    "Screen: selectLine with scrollback",
    "Screen: selectionString basic",
    "Screen: selectionString start outside of written area",
    "Screen: selectionString end outside of written area",
    "Screen: selectionString trim space",
    "Screen: selectionString trim empty line",
    "Screen: selectionString soft wrap",
    "Screen: selectionString wide char",
    "Screen: selectionString wide char with header",
    "Screen: selectionString empty with soft wrap",
    "Screen: selectionString with zero width joiner",
    "Screen: selectionString, rectangle, basic",
    "Screen: selectionString, rectangle, w/EOL",
    "Screen: selectionString, rectangle, more complex w/breaks",
    "Screen: selectionString multi-page",
)


def select(terminal, start, end, rectangular=False):
    terminal.select_start(*start)
    if rectangular:
        terminal.select_rectangular()
    terminal.select_update(*end)
    return terminal.select_finish()


def select_line(terminal, column, row):
    terminal.select_start(column, row)
    terminal.select_extend(column, row, cycle=True)
    terminal.select_extend(column, row, cycle=True)
    return terminal.select_finish()


class GhosttyScreenSelectionTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_screen_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 20)
        self.assertEqual(len(set(UPSTREAM_CASES)), 20)

    def test_hyperlink_start_and_end_affect_only_enclosed_cells(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(
                b"\x1b]8;;https://example.test/a\x1b\\A"
                b"\x1b]8;;\x1b\\B"
            )

            self.assertEqual(terminal.hyperlink(0, 0), "https://example.test/a")
            self.assertEqual(terminal.hyperlink(1, 0), "")
            self.assertEqual(terminal.hyperlink_count(), 1)

    def test_hyperlink_accepts_its_current_explicit_values(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(
                b"\x1b]8;id=current;https://example.test/a\x1b\\A"
                b"\x1b]8;id=current;https://example.test/a\x1b\\B"
                b"\x1b]8;;\x1b\\"
            )
            snapshot = terminal.snapshot()

            self.assertNotEqual(snapshot.cell(0, 0).hyperlink, 0)
            self.assertEqual(
                snapshot.cell(0, 0).hyperlink,
                snapshot.cell(1, 0).hyperlink,
            )
            self.assertEqual(terminal.hyperlink_count(), 1)

    def test_hyperlink_reuses_an_equal_implicit_value_while_active(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(
                b"\x1b]8;;https://example.test/a\x1b\\A"
                b"\x1b]8;;https://example.test/a\x1b\\B"
                b"\x1b]8;;\x1b\\"
            )
            snapshot = terminal.snapshot()

            self.assertNotEqual(snapshot.cell(0, 0).hyperlink, 0)
            self.assertEqual(
                snapshot.cell(0, 0).hyperlink,
                snapshot.cell(1, 0).hyperlink,
            )
            self.assertEqual(terminal.hyperlink_count(), 1)

    def test_line_selection_covers_the_written_line(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(put_rows(b"ABC  DEF", b" 123", b"456"))
            self.assertEqual(select_line(terminal, 3, 0), b"ABC  DEF")

    def test_line_selection_joins_a_fully_soft_wrapped_line(self):
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(b"1ABCD2EFGH\r\n3IJKL")
            self.assertEqual(select_line(terminal, 2, 1), b"1ABCD2EFGH")

    def test_line_selection_works_in_scrollback(self):
        with Shitty(columns=2, rows=3, save_lines=5) as terminal:
            terminal.write(b"1A\r\n2B\r\n3C\r\n4D\r\n5E")
            terminal.page_up()
            self.assertEqual(
                [line.rstrip() for line in terminal.snapshot().lines],
                ["2B", "3C", "4D"],
            )
            self.assertEqual(select_line(terminal, 0, 0), b"2B")

    def test_selection_string_basic(self):
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write(put_rows(b"1ABCD", b"2EFGH", b"3IJKL"))
            self.assertEqual(select(terminal, (0, 1), (3, 2)), b"2EFGH\n3IJ")

    def test_selection_string_trimmed_start_outside_written_area(self):
        with Shitty(columns=5, rows=10) as terminal:
            terminal.write(put_rows(b"1ABCD", b"2EFGH", b"3IJKL"))
            self.assertEqual(select(terminal, (0, 5), (3, 6)), b"")

    def test_selection_string_trimmed_end_outside_written_area(self):
        with Shitty(columns=5, rows=10) as terminal:
            terminal.write(put_rows(b"1ABCD", b"2EFGH", b"3IJKL"))
            self.assertEqual(select(terminal, (0, 2), (3, 6)), b"3IJKL")

    @unittest.expectedFailure
    def test_selection_string_trim_space_policy(self):
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write(put_rows(b"1AB  ", b"2EFGH", b"3IJKL"))
            self.assertEqual(select(terminal, (0, 0), (3, 1)), b"1AB\n2EF")

    def test_selection_string_no_trim_preserves_written_space(self):
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write(put_rows(b"1AB  ", b"2EFGH", b"3IJKL"))
            self.assertEqual(
                select(terminal, (0, 0), (3, 1)),
                b"1AB  \n2EF",
            )

    @unittest.expectedFailure
    def test_selection_string_trim_empty_line_policy(self):
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(put_rows(b"1AB  ", b"", b"2EFGH", b"3IJKL"))
            self.assertEqual(select(terminal, (0, 0), (3, 2)), b"1AB\n\n2EF")

    def test_selection_string_no_trim_keeps_written_space_before_empty_line(self):
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(put_rows(b"1AB  ", b"", b"2EFGH", b"3IJKL"))
            self.assertEqual(
                select(terminal, (0, 0), (3, 2)),
                b"1AB  \n\n2EF",
            )

    def test_selection_string_soft_wrap_has_no_inserted_newline(self):
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write(b"1ABCD2EFGH3IJKL")
            self.assertEqual(select(terminal, (0, 1), (3, 2)), b"2EFGH3IJ")

    def test_selection_string_expands_every_half_of_a_wide_character(self):
        text = "1A⚡".encode()
        cases = (
            ((0, 0), (4, 0), text),
            ((0, 0), (3, 0), text),
            ((3, 0), (4, 0), "⚡".encode()),
        )
        for start, end, expected in cases:
            with self.subTest(start=start, end=end):
                with Shitty(columns=5, rows=3) as terminal:
                    terminal.write(text)
                    self.assertEqual(select(terminal, start, end), expected)

    @unittest.expectedFailure
    def test_selection_string_wide_prewrap_header_policy(self):
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write("1ABC⚡".encode())
            self.assertEqual(
                select(terminal, (0, 0), (5, 0)),
                "1ABC⚡".encode(),
            )

    @unittest.expectedFailure
    def test_selection_string_trimmed_wide_tail_on_soft_wrap(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write("👨".encode() + b"      ")
            self.assertEqual(
                select(terminal, (1, 0), (3, 0)),
                "👨".encode(),
            )

    def test_selection_string_keeps_a_trailing_zero_width_joiner(self):
        text = "👨‍".encode()
        with Shitty(columns=10, rows=1) as terminal:
            terminal.write(text)
            self.assertEqual(select(terminal, (0, 0), (2, 0)), text)

    def test_selection_string_rectangular_basic(self):
        rows = (
            b"Lorem ipsum dolor",
            b"sit amet, consectetur",
            b"adipiscing elit, sed do",
            b"eiusmod tempor incididunt",
            b"ut labore et dolore",
        )
        with Shitty(columns=30, rows=5) as terminal:
            terminal.write(put_rows(*rows))
            self.assertEqual(
                select(terminal, (2, 1), (7, 3), rectangular=True),
                b"t ame\nipisc\nusmod",
            )

    def test_selection_string_rectangular_trim_at_end_of_line(self):
        rows = (
            b"Lorem ipsum dolor",
            b"sit amet, consectetur",
            b"adipiscing elit, sed do",
            b"eiusmod tempor incididunt",
            b"ut labore et dolore",
        )
        with Shitty(columns=30, rows=5) as terminal:
            terminal.write(put_rows(*rows))
            self.assertEqual(
                select(terminal, (12, 0), (27, 4), rectangular=True),
                (
                    b"dolor\n"
                    b"nsectetur\n"
                    b"lit, sed do\n"
                    b"or incididunt\n"
                    b" dolore"
                ),
            )

    def test_selection_string_rectangular_trim_with_blank_rows(self):
        rows = (
            b"Lorem ipsum dolor",
            b"sit amet, consectetur",
            b"adipiscing elit, sed do",
            b"eiusmod tempor incididunt",
            b"ut labore et dolore",
            b"",
            b"magna aliqua. Ut enim",
            b"ad minim veniam, quis",
        )
        with Shitty(columns=30, rows=8) as terminal:
            terminal.write(put_rows(*rows))
            self.assertEqual(
                select(terminal, (11, 2), (27, 7), rectangular=True),
                (
                    b"elit, sed do\n"
                    b"por incididunt\n"
                    b"t dolore\n\n"
                    b"a. Ut enim\n"
                    b"niam, quis"
                ),
            )

    def test_selection_string_across_long_lived_storage(self):
        with Shitty(columns=10, rows=3, save_lines=400) as terminal:
            terminal.write(
                b"".join(f"{index}\r\n".encode() for index in range(299))
                + b"299"
            )
            terminal.wheel_up()
            self.assertEqual(
                [line.rstrip() for line in terminal.snapshot().lines],
                ["296", "297", "298"],
            )
            self.assertEqual(
                select(terminal, (0, 0), (3, 2)),
                b"296\n297\n298",
            )


if __name__ == "__main__":
    unittest.main()
