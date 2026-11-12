# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


UPSTREAM_CASES = (
    "PageList pageIterator reverse history two pages",
    "PageList PageIterator reverse count includes row zero",
    "PageList PageIterator count crosses page boundaries",
    "PageList cellIterator",
    "PageList cellIterator reverse",
    "PageList promptIterator left_up",
    "PageList promptIterator right_down",
    "PageList promptIterator right_down continuation at start",
    "PageList promptIterator right_down with prompt before continuation",
    "PageList promptIterator right_down limit inclusive",
    "PageList promptIterator left_up limit inclusive",
    "PageList highlightSemanticContent prompt",
    "PageList highlightSemanticContent prompt with output",
    "PageList highlightSemanticContent prompt multiline",
    "PageList highlightSemanticContent prompt only",
    "PageList highlightSemanticContent prompt to end of screen",
    "PageList highlightSemanticContent input basic",
    "PageList highlightSemanticContent input with output",
    "PageList highlightSemanticContent input multiline with continuation",
    "PageList highlightSemanticContent input no input returns null",
)


PROMPT = 1
INPUT = 2
OUTPUT = 3


def osc133(action, options=b""):
    suffix = b";" + options if options else b""
    return b"\x1b]133;" + action + suffix + b"\x1b\\"


def numbered_lines(first, last, width=3):
    return b"\r\n".join(
        str(value).zfill(width).encode()
        for value in range(first, last + 1)
    )


def visible_lines(terminal):
    return tuple(line.rstrip() for line in terminal.snapshot().lines)


def reverse_selection(terminal, start, end=(0, 0)):
    terminal.select_start(*start)
    terminal.select_update(*end)
    return terminal.select_finish()


def select_semantic_output(terminal, column, row):
    terminal.select_start(column, row)
    terminal.select_extend(column, row, cycle=True)
    terminal.select_extend(column, row, cycle=True)
    return terminal.select_finish()


def cells(terminal, row, start, end):
    snapshot = terminal.snapshot()
    return tuple(
        (snapshot.cell(column, row).char, snapshot.cell(column, row).semantic)
        for column in range(start, end)
    )


class GhosttyPageListSemanticIterationTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 20)
        self.assertEqual(len(set(UPSTREAM_CASES)), 20)

    def test_reverse_history_traversal_keeps_retained_rows_in_logical_order(self):
        with Shitty(columns=4, rows=4, save_lines=40) as terminal:
            terminal.write(numbered_lines(0, 19))
            terminal.wheel_up(100)

            self.assertEqual(visible_lines(terminal), ("000", "001", "002", "003"))
            self.assertEqual(
                reverse_selection(terminal, (3, 3)),
                b"000\n001\n002\n003",
            )

    def test_reverse_single_row_count_includes_the_first_screen_cell(self):
        with Shitty(columns=2, rows=2, save_lines=0) as terminal:
            terminal.write(b"AB")

            self.assertEqual(reverse_selection(terminal, (2, 0)), b"AB")

    def test_reverse_traversal_crosses_internal_storage_boundaries_once(self):
        with Shitty(columns=4, rows=300, save_lines=0) as terminal:
            terminal.write(numbered_lines(0, 299))

            self.assertEqual(
                reverse_selection(terminal, (3, 299)).decode().splitlines(),
                [f"{value:03}" for value in range(300)],
            )

    def test_forward_cell_traversal_is_row_major(self):
        with Shitty(columns=2, rows=2, save_lines=0) as terminal:
            terminal.write(b"01\r\n01")
            snapshot = terminal.snapshot()

            self.assertEqual(tuple(snapshot.lines), ("01", "01"))
            self.assertEqual(
                tuple(cell.char for cell in snapshot.cells),
                ("0", "1", "0", "1"),
            )

    def test_reverse_cell_traversal_preserves_the_same_logical_extent(self):
        with Shitty(columns=2, rows=2, save_lines=0) as terminal:
            terminal.write(b"01\r\n01")

            self.assertEqual(reverse_selection(terminal, (2, 1)), b"01\n01")

    @unittest.expectedFailure
    def test_output_selection_finds_the_nearest_prompt_when_scanning_up(self):
        with Shitty(columns=10, rows=8, save_lines=10) as terminal:
            terminal.write(
                osc133(b"P") + b"$ old" + osc133(b"B") + b"\r\ncmd0"
                + osc133(b"C") + b"\r\nout0a\r\nout0b\r\n"
                + osc133(b"P") + b"$ new" + osc133(b"B") + b"\r\ncmd1"
                + osc133(b"C") + b"\r\nout1a\r\nout1b"
            )

            self.assertEqual(
                select_semantic_output(terminal, 2, 7),
                b"out1a\nout1b",
            )

    @unittest.expectedFailure
    def test_output_selection_scans_down_to_the_first_prompt_without_a_prior_one(self):
        with Shitty(columns=10, rows=6, save_lines=0) as terminal:
            terminal.write(
                b"orphan-a\r\norphan-b\r\n"
                + osc133(b"P") + b"$ prompt"
            )

            self.assertEqual(
                select_semantic_output(terminal, 2, 0),
                b"orphan-a\norphan-b",
            )

    @unittest.expectedFailure
    def test_output_selection_accepts_a_continuation_at_the_screen_start(self):
        with Shitty(columns=10, rows=6, save_lines=0) as terminal:
            terminal.write(
                osc133(b"P", b"k=c") + b"> "
                + osc133(b"B") + b"continued"
                + osc133(b"C") + b"\r\nresult-a\r\nresult-b\r\n"
                + osc133(b"P") + b"$ next"
            )

            self.assertEqual(
                select_semantic_output(terminal, 2, 2),
                b"result-a\nresult-b",
            )

    @unittest.expectedFailure
    def test_output_selection_treats_a_continuation_start_as_its_local_prompt(self):
        with Shitty(columns=10, rows=7, save_lines=0) as terminal:
            terminal.write(
                osc133(b"P") + b"$ head\r\n"
                + osc133(b"P", b"k=c") + b"> "
                + osc133(b"B") + b"continued"
                + osc133(b"C") + b"\r\nlocal-a\r\nlocal-b\r\n"
                + osc133(b"P") + b"$ next"
            )

            self.assertEqual(
                select_semantic_output(terminal, 2, 3),
                b"local-a\nlocal-b",
            )

    @unittest.expectedFailure
    def test_output_selection_includes_a_next_prompt_at_the_search_limit(self):
        with Shitty(columns=10, rows=6, save_lines=0) as terminal:
            terminal.write(
                osc133(b"P") + b"$ one" + osc133(b"B") + b" cmd"
                + osc133(b"C") + b"\r\nfirst-a\r\nfirst-b\r\n"
                + osc133(b"P") + b"$ two"
            )

            self.assertEqual(
                select_semantic_output(terminal, 2, 1),
                b"first-a\nfirst-b",
            )

    @unittest.expectedFailure
    def test_output_selection_includes_a_prior_prompt_at_the_search_limit(self):
        with Shitty(columns=10, rows=7, save_lines=0) as terminal:
            terminal.write(
                osc133(b"P") + b"$ zero" + osc133(b"B") + b" cmd0"
                + osc133(b"C") + b"\r\nzero-a\r\nzero-b\r\n"
                + osc133(b"P") + b"$ one" + osc133(b"B") + b" cmd1"
                + osc133(b"C") + b"\r\none-a\r\none-b"
            )

            self.assertEqual(
                select_semantic_output(terminal, 2, 5),
                b"one-a\none-b",
            )

    def test_prompt_highlight_metadata_covers_prompt_and_input(self):
        with Shitty(columns=10, rows=2, save_lines=0) as terminal:
            terminal.write(osc133(b"P") + b"AAAAA" + osc133(b"B") + b"BBB")

            self.assertEqual(
                cells(terminal, 0, 0, 8),
                (("A", PROMPT),) * 5 + (("B", INPUT),) * 3,
            )

    def test_prompt_highlight_metadata_stops_when_output_begins(self):
        with Shitty(columns=10, rows=2, save_lines=0) as terminal:
            terminal.write(
                osc133(b"P") + b"$$$"
                + osc133(b"B") + b"llll"
                + osc133(b"C") + b"ooo"
            )

            self.assertEqual(
                cells(terminal, 0, 0, 10),
                (("$", PROMPT),) * 3
                + (("l", INPUT),) * 4
                + (("o", OUTPUT),) * 3,
            )

    def test_prompt_highlight_metadata_spans_a_soft_wrapped_input(self):
        with Shitty(columns=10, rows=3, save_lines=0) as terminal:
            terminal.write(
                osc133(b"P") + b"$" * 10
                + osc133(b"B") + b"c" * 5
            )

            self.assertEqual(cells(terminal, 0, 0, 10), (("$", PROMPT),) * 10)
            self.assertEqual(cells(terminal, 1, 0, 5), (("c", INPUT),) * 5)

    def test_prompt_only_highlight_metadata_has_no_input_cells(self):
        with Shitty(columns=10, rows=3, save_lines=0) as terminal:
            terminal.write(osc133(b"P") + b"$$$$$" + b"\r\n" + osc133(b"P"))

            self.assertEqual(cells(terminal, 0, 0, 5), (("$", PROMPT),) * 5)
            self.assertNotIn(INPUT, tuple(value for _, value in cells(terminal, 0, 0, 10)))

    def test_final_prompt_highlight_metadata_extends_through_final_input(self):
        with Shitty(columns=10, rows=2, save_lines=0) as terminal:
            terminal.write(
                osc133(b"P") + b"$$$"
                + osc133(b"B") + b"ccccc"
            )

            self.assertEqual(
                cells(terminal, 0, 0, 8),
                (("$", PROMPT),) * 3 + (("c", INPUT),) * 5,
            )

    def test_input_highlight_metadata_starts_after_the_prompt(self):
        with Shitty(columns=10, rows=2, save_lines=0) as terminal:
            terminal.write(
                osc133(b"P") + b"$$$"
                + osc133(b"B") + b"lllll"
            )

            self.assertEqual(cells(terminal, 0, 3, 8), (("l", INPUT),) * 5)
            self.assertEqual(cells(terminal, 0, 0, 3), (("$", PROMPT),) * 3)

    def test_input_highlight_metadata_stops_before_output(self):
        with Shitty(columns=10, rows=2, save_lines=0) as terminal:
            terminal.write(
                osc133(b"P") + b"$$"
                + osc133(b"B") + b"ccc"
                + osc133(b"C") + b"ooooo"
            )

            self.assertEqual(cells(terminal, 0, 2, 5), (("c", INPUT),) * 3)
            self.assertEqual(cells(terminal, 0, 5, 10), (("o", OUTPUT),) * 5)

    def test_input_highlight_metadata_crosses_a_continuation_prompt(self):
        with Shitty(columns=10, rows=3, save_lines=0) as terminal:
            terminal.write(
                osc133(b"P") + b"$$"
                + osc133(b"B") + b"c" * 8
                + osc133(b"P", b"k=c") + b">>"
                + osc133(b"B") + b"d" * 4
            )

            self.assertEqual(cells(terminal, 0, 2, 10), (("c", INPUT),) * 8)
            self.assertEqual(cells(terminal, 1, 0, 2), ((">", PROMPT),) * 2)
            self.assertEqual(cells(terminal, 1, 2, 6), (("d", INPUT),) * 4)

    def test_input_highlight_metadata_is_absent_when_output_follows_prompt(self):
        with Shitty(columns=10, rows=2, save_lines=0) as terminal:
            terminal.write(
                osc133(b"P") + b"$$$"
                + osc133(b"C") + b"ooooooo"
            )

            semantic = tuple(value for _, value in cells(terminal, 0, 0, 10))
            self.assertEqual(semantic, (PROMPT,) * 3 + (OUTPUT,) * 7)
            self.assertNotIn(INPUT, semantic)


if __name__ == "__main__":
    unittest.main()
