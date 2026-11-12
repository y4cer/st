# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


UPSTREAM_CASES = (
    "PageList plain single line",
    "PageList plain spanning two pages",
    "PageList soft-wrapped line spanning two pages without unwrap",
    "PageList soft-wrapped line spanning two pages with unwrap",
    "PageList VT spanning two pages",
    "PageList plain with x offset on single page",
    "PageList plain with x offset spanning two pages",
    "PageList plain with start_x only",
    "PageList plain with end_x only",
    "PageList plain rectangle basic",
    "PageList plain rectangle with EOL",
    "PageList plain rectangle more complex with breaks",
    "TerminalFormatter plain no selection",
    "TerminalFormatter vt with palette",
    "TerminalFormatter with selection",
    "TerminalFormatter plain with pin_map",
    "TerminalFormatter plain multiline with pin_map",
    "TerminalFormatter vt with palette and pin_map",
    "TerminalFormatter with selection and pin_map",
    "Screen plain single line",
)


def select(terminal, start, end, rectangular=False):
    terminal.select_start(*start)
    if rectangular:
        terminal.select_rectangular()
    terminal.select_update(*end)
    return terminal.select_finish()


def palette_query(terminal, *indices):
    terminal.write(
        b"\x1b]4;" + b";".join(f"{index};?".encode() for index in indices) + b"\x1b\\"
    )
    return terminal.read_input()


RECTANGLE_ROWS = (
    b"Lorem ipsum dolor",
    b"sit amet, consectetur",
    b"adipiscing elit, sed do",
    b"eiusmod tempor incididunt",
    b"ut labore et dolore",
)


def write_rows(terminal, rows):
    terminal.write(b"\r\n".join(rows))


class GhosttyFormatterPageListTerminalTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 20)
        self.assertEqual(len(set(UPSTREAM_CASES)), 20)

    def test_pagelist_plain_single_line_copies_every_character(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"hello, world")

            self.assertEqual(select(terminal, (0, 0), (12, 0)), b"hello, world")

    def test_plain_copy_spans_a_high_backing_storage_boundary(self):
        with Shitty(columns=80, rows=300, save_lines=0) as terminal:
            terminal.write(b"\x1b[255;1Hpage one\r\npage two")

            self.assertEqual(select(terminal, (0, 254), (8, 255)), b"page one\npage two")

    def test_physical_soft_wrap_survives_a_high_backing_storage_boundary(self):
        with Shitty(columns=10, rows=300, save_lines=0) as terminal:
            terminal.write(b"\x1b[255;1Hhello world test")

            self.assertEqual(terminal.all_text()[254:256], ("hello worl", "d test"))

    def test_logical_copy_unwraps_across_a_high_backing_storage_boundary(self):
        with Shitty(columns=10, rows=300, save_lines=0) as terminal:
            terminal.write(b"\x1b[255;1Hhello world test")

            self.assertEqual(
                select(terminal, (0, 254), (6, 255)),
                b"hello world test",
            )

    def test_sgr_state_survives_a_hard_row_across_high_backing_storage(self):
        with Shitty(columns=80, rows=300, save_lines=0) as terminal:
            terminal.write(b"\x1b[255;1H\x1b[1mpage one\r\npage two")
            snapshot = terminal.snapshot()

            self.assertTrue(all(snapshot.cell(column, 254).bold for column in range(8)))
            self.assertTrue(all(snapshot.cell(column, 255).bold for column in range(8)))

    def test_partial_first_and_last_rows_copy_on_one_screen(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"hello world\r\ntest case\r\nfoo bar")

            self.assertEqual(
                select(terminal, (6, 0), (3, 2)),
                b"world\ntest case\nfoo",
            )

    def test_partial_rows_copy_across_high_backing_storage(self):
        with Shitty(columns=80, rows=300, save_lines=0) as terminal:
            terminal.write(b"\x1b[255;1Hhello world\r\nfoo bar test")

            self.assertEqual(select(terminal, (6, 254), (3, 255)), b"world\nfoo")

    def test_start_column_without_an_end_copies_the_remaining_text(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"hello world")

            self.assertEqual(select(terminal, (6, 0), (80, 23)), b"world")

    def test_end_column_without_a_start_keeps_prior_full_rows(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"hello world\r\ntest")

            self.assertEqual(select(terminal, (0, 0), (3, 1)), b"hello world\ntes")

    def test_rectangular_copy_uses_the_same_five_columns_on_each_row(self):
        with Shitty(columns=30, rows=5, save_lines=0) as terminal:
            write_rows(terminal, RECTANGLE_ROWS)

            self.assertEqual(
                select(terminal, (2, 1), (7, 3), rectangular=True),
                b"t ame\nipisc\nusmod",
            )

    def test_rectangular_copy_stops_each_row_at_its_drawn_eol(self):
        with Shitty(columns=30, rows=5, save_lines=0) as terminal:
            write_rows(terminal, RECTANGLE_ROWS)

            self.assertEqual(
                select(terminal, (12, 0), (27, 4), rectangular=True),
                b"dolor\nnsectetur\nlit, sed do\nor incididunt\n dolore",
            )

    def test_rectangular_copy_preserves_an_interior_blank_row(self):
        rows = RECTANGLE_ROWS + (b"", b"magna aliqua. Ut enim", b"ad minim veniam, quis")
        with Shitty(columns=30, rows=8, save_lines=0) as terminal:
            write_rows(terminal, rows)

            self.assertEqual(
                select(terminal, (11, 2), (27, 7), rectangular=True),
                b"elit, sed do\npor incididunt\nt dolore\n\na. Ut enim\nniam, quis",
            )

    def test_terminal_plain_copy_without_a_selection_uses_all_content(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"hello\r\nworld")

            self.assertEqual(select(terminal, (0, 0), (80, 23)), b"hello\nworld")

    def test_palette_query_output_replays_the_same_palette_in_another_terminal(self):
        with Shitty(columns=80, rows=24, save_lines=0) as source:
            source.write(
                b"\x1b]4;0;rgb:12/34/56\x1b\\"
                b"\x1b]4;1;rgb:ab/cd/ef\x1b\\"
                b"\x1b]4;255;rgb:ff/00/ff\x1b\\test"
            )
            serialized = palette_query(source, 0, 1, 255)

            with Shitty(columns=80, rows=24, save_lines=0) as replay:
                replay.write(serialized)
                self.assertEqual(palette_query(replay, 0, 1, 255), serialized)

    def test_terminal_formatter_selection_maps_to_public_copy(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"line1\r\nline2\r\nline3")

            self.assertEqual(select(terminal, (0, 1), (5, 1)), b"line2")

    def test_single_line_copy_maps_each_byte_to_its_selected_column(self):
        text = b"hello, world"
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(text)

            for column, byte in enumerate(text):
                with self.subTest(column=column):
                    self.assertEqual(
                        select(terminal, (column, 0), (column + 1, 0)),
                        bytes((byte,)),
                    )

    def test_multiline_copy_maps_text_to_rows_around_the_line_separator(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"hello\r\nworld")

            self.assertEqual(select(terminal, (0, 0), (5, 1)), b"hello\nworld")
            for row, text in enumerate((b"hello", b"world")):
                for column, byte in enumerate(text):
                    with self.subTest(row=row, column=column):
                        self.assertEqual(
                            select(terminal, (column, row), (column + 1, row)),
                            bytes((byte,)),
                        )

    def test_palette_query_serialization_does_not_move_or_rewrite_content(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"\x1b]4;0;rgb:12/34/56\x1b\\test")
            before = terminal.snapshot()

            response = palette_query(terminal, 0)
            after = terminal.snapshot()

            self.assertIn(b"\x1b]4;0;rgb:1212/3434/5656\x1b\\", response)
            self.assertEqual((after.cursor_x, after.cursor_y), (before.cursor_x, before.cursor_y))
            self.assertEqual(after.lines, before.lines)

    def test_selection_copy_maps_each_selected_byte_to_its_row_and_column(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"line1\r\nline2\r\nline3")

            for column, byte in enumerate(b"line2"):
                with self.subTest(column=column):
                    self.assertEqual(
                        select(terminal, (column, 1), (column + 1, 1)),
                        bytes((byte,)),
                    )

    def test_active_screen_plain_copy_contains_its_single_line(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"hello, world")

            self.assertEqual(select(terminal, (0, 0), (80, 23)), b"hello, world")


if __name__ == "__main__":
    unittest.main()
