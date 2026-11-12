# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty, put_rows


UPSTREAM_CASES = (
    "Screen: selectAll",
    "Screen: selectLine across soft-wrap",
    "Screen: selectLine across soft-wrap ignores blank lines",
    "Screen: selectLine disabled whitespace trimming",
    "Screen: selectLine semantic prompt boundary",
    "Screen: selectLine semantic prompt to input boundary",
    "Screen: selectLine semantic input to output boundary",
    "Screen: selectLine semantic mid-row boundary",
    "Screen: selectLine semantic boundary soft-wrap with mid-row transition",
    "Screen: selectLine semantic boundary disabled",
    "Screen: selectLine semantic boundary first cell of row",
    "Screen: selectLine semantic boundary across mixed-width pages",
    "Screen: selectLine semantic all same content",
    "Screen: selectWord",
    "Screen: selectWord across soft-wrap",
    "Screen: selectWord whitespace across soft-wrap",
    "Screen: selectWord with character boundary",
    "Screen: selectOutput",
    "Screen: lineIterator",
    "Screen: lineIterator soft wrap",
)


def osc133(action):
    return b"\x1b]133;" + action + b"\x1b\\"


def select_range(terminal, start, end):
    terminal.select_start(*start)
    terminal.select_update(*end)
    return terminal.select_finish()


def select_word(terminal, column, row):
    terminal.select_start(column, row)
    terminal.select_extend(column, row, cycle=True)
    return terminal.select_finish()


def select_line(terminal, column, row):
    terminal.select_start(column, row)
    terminal.select_extend(column, row, cycle=True)
    terminal.select_extend(column, row, cycle=True)
    return terminal.select_finish()


class GhosttyScreenSemanticSelectionTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_screen_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 20)
        self.assertEqual(len(set(UPSTREAM_CASES)), 20)

    def test_select_all_extent_through_the_public_drag_operation(self):
        with Shitty(columns=10, rows=10, save_lines=0) as terminal:
            terminal.write(put_rows(b"ABC  DEF", b" 123", b"456"))
            self.assertEqual(
                select_range(terminal, (0, 0), (3, 2)),
                b"ABC  DEF\n 123\n456",
            )

            terminal.write(
                put_rows(
                    b"ABC  DEF",
                    b" 123",
                    b"456",
                    b"",
                    b"FOO",
                    b" BAR",
                    b" BAZ",
                    b" QWERTY",
                    b" 12345678",
                )
            )
            self.assertEqual(
                select_range(terminal, (0, 0), (9, 8)),
                (
                    b"ABC  DEF\n 123\n456\n\nFOO\n BAR\n BAZ\n"
                    b" QWERTY\n 12345678"
                ),
            )

    @unittest.expectedFailure
    def test_line_selection_trims_a_partly_filled_soft_wrapped_line(self):
        with Shitty(columns=5, rows=10) as terminal:
            terminal.write(b" 12 34012   \r\n 123")
            self.assertEqual(select_line(terminal, 1, 0), b"12 34012")

    @unittest.expectedFailure
    def test_line_selection_ignores_blank_soft_wrapped_tail_rows(self):
        with Shitty(columns=5, rows=10) as terminal:
            terminal.write(b" 12 34012             \r\n 123")
            results = (
                select_line(terminal, 1, 0),
                select_line(terminal, 1, 1),
                select_line(terminal, 3, 0),
            )
            self.assertEqual(results, (b"12 34012",) * 3)

    def test_line_selection_can_retain_the_untrimmed_logical_extent(self):
        with Shitty(columns=5, rows=10) as terminal:
            terminal.write(b" 12 34012   \r\n 123")
            terminal.select_start(1, 0)
            terminal.select_extend(1, 0, cycle=True)
            terminal.select_extend(1, 0, cycle=True)
            self.assertEqual(
                terminal.selection_state()["snapped"],
                (0, 0, 5, 2),
            )

            terminal.select_start(1, 3)
            terminal.select_extend(1, 3, cycle=True)
            terminal.select_extend(1, 3, cycle=True)
            self.assertEqual(
                terminal.selection_state()["snapped"],
                (0, 3, 5, 3),
            )

    @unittest.expectedFailure
    def test_line_selection_stops_at_a_prompt_boundary_after_soft_wrap(self):
        with Shitty(columns=5, rows=10) as terminal:
            terminal.write(
                b"ABCDE\r\n"
                + osc133(b"P")
                + b"A    "
                + osc133(b"C")
                + b"> "
            )
            results = (
                select_line(terminal, 1, 1),
                select_line(terminal, 1, 2),
            )
            self.assertEqual(results, (b"A", b">"))

    @unittest.expectedFailure
    def test_line_selection_separates_prompt_and_input_on_one_row(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(osc133(b"P") + b"$>" + osc133(b"B") + b"command")
            results = (
                select_line(terminal, 0, 0),
                select_line(terminal, 5, 0),
            )
            self.assertEqual(results, (b"$>", b"command"))

    def test_line_selection_keeps_hard_line_input_and_output_separate(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(
                osc133(b"B")
                + b"ls -la\r\n"
                + osc133(b"C")
                + b"file.txt"
            )
            results = (
                select_line(terminal, 2, 0),
                select_line(terminal, 2, 1),
            )
            self.assertEqual(results, (b"ls -la", b"file.txt"))

    @unittest.expectedFailure
    def test_line_selection_stops_at_every_mid_row_semantic_boundary(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(
                osc133(b"C")
                + b"out"
                + osc133(b"P")
                + b"$>"
                + osc133(b"B")
                + b"cmd"
            )
            results = (
                select_line(terminal, 1, 0),
                select_line(terminal, 3, 0),
                select_line(terminal, 6, 0),
            )
            self.assertEqual(results, (b"out", b"$>", b"cmd"))

    @unittest.expectedFailure
    def test_semantic_line_selection_crosses_wrap_but_not_a_mid_row_transition(self):
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(
                osc133(b"P")
                + b"$ "
                + osc133(b"B")
                + b"cmd12"
                + osc133(b"C")
                + b"out"
            )
            results = (
                select_line(terminal, 3, 0),
                select_line(terminal, 0, 1),
                select_line(terminal, 3, 1),
            )
            self.assertEqual(results, (b"cmd12", b"cmd12", b"out"))

    def test_line_selection_without_semantic_boundaries_takes_the_whole_line(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(osc133(b"P") + b"$ " + osc133(b"B") + b"command")
            self.assertEqual(select_line(terminal, 0, 0), b"$ command")

    @unittest.expectedFailure
    def test_semantic_boundary_at_the_first_cell_splits_a_soft_wrap(self):
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(osc133(b"B") + b"12345" + osc133(b"C") + b"ABCDE")
            results = (
                select_line(terminal, 2, 0),
                select_line(terminal, 2, 1),
            )
            self.assertEqual(results, (b"12345", b"ABCDE"))

    @unittest.expectedFailure
    def test_semantic_boundary_survives_public_mixed_width_reflow(self):
        with Shitty(columns=4, rows=3, save_lines=4) as terminal:
            terminal.write(osc133(b"B") + b"ABCD" + osc133(b"C") + b"E")
            terminal.resize(2, 3)
            terminal.resize(4, 3)
            results = (
                select_line(terminal, 1, 0),
                select_line(terminal, 0, 1),
            )
            self.assertEqual(results, (b"ABCD", b"E"))

    def test_line_selection_crosses_wrap_when_semantic_content_is_uniform(self):
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(osc133(b"P") + b"prompt text")
            self.assertEqual(select_line(terminal, 2, 1), b"prompt text")

    def test_word_selection_handles_words_whitespace_and_screen_end(self):
        with Shitty(columns=10, rows=10) as terminal:
            terminal.write(put_rows(b"ABC  DEF", b" 123", b"456"))
            results = (
                select_word(terminal, 0, 0),
                select_word(terminal, 2, 0),
                select_word(terminal, 1, 0),
                select_word(terminal, 3, 0),
                select_word(terminal, 0, 1),
                select_word(terminal, 1, 2),
            )
            self.assertEqual(results, (b"ABC", b"ABC", b"ABC", b"  ", b" ", b"456"))

    def test_word_selection_crosses_a_soft_wrap_in_both_directions(self):
        with Shitty(columns=5, rows=10) as terminal:
            terminal.write(b" 1234012\r\n 123")
            results = (
                select_word(terminal, 1, 0),
                select_word(terminal, 1, 1),
                select_word(terminal, 3, 0),
            )
            self.assertEqual(results, (b"1234012",) * 3)

    @unittest.expectedFailure
    def test_whitespace_word_selection_crosses_a_soft_wrap(self):
        with Shitty(columns=5, rows=10) as terminal:
            terminal.write(b"1       1\r\n 123")
            results = (
                select_word(terminal, 1, 0),
                select_word(terminal, 1, 1),
                select_word(terminal, 3, 0),
            )
            self.assertEqual(results, (b"       ",) * 3)

    @unittest.expectedFailure
    def test_word_selection_uses_ghostty_character_boundaries(self):
        boundaries = "'\"│`|:;,()[]{}<>$"
        actual = []
        expected = []
        for boundary in boundaries:
            with Shitty(columns=20, rows=2) as terminal:
                terminal.write(f" {boundary}abc{boundary} ".encode())
                actual.append(
                    (
                        select_word(terminal, 2, 0),
                        select_word(terminal, 4, 0),
                        select_word(terminal, 3, 0),
                        select_word(terminal, 1, 0),
                    )
                )
                expected.append(
                    (
                        b"abc",
                        b"abc",
                        b"abc",
                        (" " + boundary).encode(),
                    )
                )
        self.assertEqual(actual, expected)

    @unittest.expectedFailure
    def test_select_output_takes_the_entire_semantic_output_block(self):
        with Shitty(columns=10, rows=15) as terminal:
            terminal.write(
                osc133(b"C")
                + b"output1\r\noutput1\r\n"
                + osc133(b"P")
                + b"prompt2\r\n"
                + osc133(b"B")
                + b"input2\r\n"
                + osc133(b"C")
                + b"output2output2output2output2\r\noutput2\r\n"
                + osc133(b"P")
                + b"$ "
                + osc133(b"B")
                + b"input3\r\n"
                + osc133(b"C")
                + b"output3\r\noutput3\r\noutput3"
            )
            actual = (
                select_line(terminal, 1, 1),
                select_line(terminal, 3, 7),
                select_line(terminal, 2, 10),
                select_line(terminal, 1, 8),
                select_line(terminal, 5, 8),
            )
            expected = (
                b"output1\noutput1",
                b"output2output2output2output2\noutput2",
                b"output3\noutput3\noutput3",
                b"",
                b"",
            )
            self.assertEqual(actual, expected)

    def test_logical_line_iteration_separates_hard_lines(self):
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(put_rows(b"1ABCD", b"2EFGH"))
            self.assertEqual(
                (select_line(terminal, 0, 0), select_line(terminal, 0, 1)),
                (b"1ABCD", b"2EFGH"),
            )

    def test_logical_line_iteration_joins_soft_wraps_only(self):
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(b"1ABCD2EFGH\r\n3ABCD")
            self.assertEqual(
                (select_line(terminal, 0, 0), select_line(terminal, 0, 2)),
                (b"1ABCD2EFGH", b"3ABCD"),
            )


if __name__ == "__main__":
    unittest.main()
