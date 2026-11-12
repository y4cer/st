# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty, put_rows


UPSTREAM_CASES = (
    "PageList highlightSemanticContent input to end of screen",
    "PageList highlightSemanticContent input prompt only returns null",
    "PageList highlightSemanticContent output basic",
    "PageList highlightSemanticContent output multiline",
    "PageList highlightSemanticContent output stops at next prompt",
    "PageList highlightSemanticContent output to end of screen",
    "PageList highlightSemanticContent output no output returns null",
    "PageList highlightSemanticContent output skips empty cells",
    "PageList erase",
    "PageList erase reaccounts page size",
    "PageList erase row with tracked pin resets to top-left",
    "PageList erase row with tracked pin shifts",
    "PageList erase row with tracked pin is erased",
    "PageList erase resets viewport to active if moves within active",
    "PageList erase resets viewport if inside erased page but not active",
    "PageList erase resets viewport to active if top is inside active",
    "PageList erase active regrows automatically",
    "PageList erase a one-row active",
    "PageList eraseRowBounded less than full row",
    "PageList eraseRowBounded with pin at top",
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


def cells(terminal, row, start, end):
    snapshot = terminal.snapshot()
    return tuple(
        (snapshot.cell(column, row).char, snapshot.cell(column, row).semantic)
        for column in range(start, end)
    )


def select_semantic_output(terminal, column, row):
    terminal.select_start(column, row)
    terminal.select_extend(column, row, cycle=True)
    terminal.select_extend(column, row, cycle=True)
    return terminal.select_finish()


class GhosttyPageListSemanticEraseTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 20)
        self.assertEqual(len(set(UPSTREAM_CASES)), 20)

    def test_final_input_zone_extends_to_the_last_written_input_cell(self):
        with Shitty(columns=10, rows=2, save_lines=0) as terminal:
            terminal.write(
                osc133(b"P") + b"$$"
                + osc133(b"B") + b"ccccc"
            )

            self.assertEqual(cells(terminal, 0, 0, 2), (("$", PROMPT),) * 2)
            self.assertEqual(cells(terminal, 0, 2, 7), (("c", INPUT),) * 5)

    def test_prompt_only_zone_contains_no_input_before_the_next_prompt(self):
        with Shitty(columns=10, rows=3, save_lines=0) as terminal:
            terminal.write(
                osc133(b"P") + b"$$$$$$$$$\r\n"
                + osc133(b"P") + b"next"
            )

            semantic = tuple(value for _, value in cells(terminal, 0, 0, 9))
            self.assertEqual(semantic, (PROMPT,) * 9)
            self.assertNotIn(INPUT, semantic)

    def test_basic_output_zone_begins_after_prompt_and_input(self):
        with Shitty(columns=10, rows=2, save_lines=0) as terminal:
            terminal.write(
                osc133(b"P") + b"$$"
                + osc133(b"B") + b"lll"
                + osc133(b"C") + b"ooo"
                + osc133(b"P")
            )

            self.assertEqual(cells(terminal, 0, 0, 2), (("$", PROMPT),) * 2)
            self.assertEqual(cells(terminal, 0, 2, 5), (("l", INPUT),) * 3)
            self.assertEqual(cells(terminal, 0, 5, 8), (("o", OUTPUT),) * 3)

    @unittest.expectedFailure
    def test_multiline_output_selection_covers_the_complete_output_zone(self):
        with Shitty(columns=10, rows=6, save_lines=0) as terminal:
            terminal.write(
                osc133(b"P") + b"$ "
                + osc133(b"B") + b"cmd"
                + osc133(b"C") + b"\r\nout-a\r\nout-b"
            )

            self.assertEqual(
                select_semantic_output(terminal, 2, 1),
                b"out-a\nout-b",
            )

    @unittest.expectedFailure
    def test_output_selection_stops_before_the_next_prompt(self):
        with Shitty(columns=10, rows=7, save_lines=0) as terminal:
            terminal.write(
                osc133(b"P") + b"$ one"
                + osc133(b"B") + b" cmd"
                + osc133(b"C") + b"\r\none-a\r\none-b\r\n"
                + osc133(b"P") + b"$ two"
            )

            self.assertEqual(
                select_semantic_output(terminal, 2, 1),
                b"one-a\none-b",
            )

    @unittest.expectedFailure
    def test_final_output_selection_extends_to_the_last_written_row(self):
        with Shitty(columns=10, rows=6, save_lines=0) as terminal:
            terminal.write(
                osc133(b"P") + b"$ "
                + osc133(b"B") + b"cmd"
                + osc133(b"C") + b"\r\nlast-a\r\nlast-b"
            )

            self.assertEqual(
                select_semantic_output(terminal, 2, 1),
                b"last-a\nlast-b",
            )

    def test_prompt_and_input_without_output_publish_no_written_output_cells(self):
        with Shitty(columns=10, rows=2, save_lines=0) as terminal:
            terminal.write(
                osc133(b"P") + b"$$$"
                + osc133(b"B") + b"ccccccc"
            )

            semantic = tuple(value for _, value in cells(terminal, 0, 0, 10))
            self.assertEqual(semantic, (PROMPT,) * 3 + (INPUT,) * 7)
            self.assertNotIn(OUTPUT, semantic)

    @unittest.expectedFailure
    def test_output_selection_skips_empty_output_cells_before_real_text(self):
        with Shitty(columns=10, rows=7, save_lines=0) as terminal:
            terminal.write(
                osc133(b"P") + b"$ "
                + osc133(b"B") + b"cmd"
                + osc133(b"C") + b"\r\n\r\nactual-a\r\nactual-b\r\n"
                + osc133(b"P") + b"$ next"
            )

            self.assertEqual(
                select_semantic_output(terminal, 2, 2),
                b"actual-a\nactual-b",
            )

    def test_erasing_history_retains_only_the_unchanged_active_screen(self):
        with Shitty(columns=6, rows=3, save_lines=30) as terminal:
            terminal.write(numbered_lines(0, 19))
            before = visible_lines(terminal)

            terminal.write(b"\x1b[3J")

            self.assertEqual(visible_lines(terminal), before)
            self.assertEqual(terminal.all_text(), before)
            self.assertEqual(terminal.scrollback_state(), (0, 3, 3, 0))

    def test_history_accounting_restarts_cleanly_after_erase(self):
        with Shitty(columns=6, rows=3, save_lines=8) as terminal:
            terminal.write(numbered_lines(0, 19))
            terminal.write(b"\x1b[3J")
            terminal.write(b"\r\n020\r\n021\r\n022")

            self.assertEqual(terminal.scrollback_state(), (3, 6, 3, 3))
            self.assertEqual(terminal.all_text(), ("017", "018", "019", "020", "021", "022"))

    def test_erasing_history_invalidates_a_selection_anchored_in_history(self):
        with Shitty(columns=6, rows=3, save_lines=8) as terminal:
            terminal.write(numbered_lines(0, 7))
            terminal.wheel_up(100)
            terminal.select_start(0, 0)
            terminal.select_update(3, 0)

            terminal.write(b"\x1b[3J")

            self.assertEqual(terminal.snapshot().selection, (-1, -1, -1, -1))
            self.assertEqual(terminal.select_finish(), b"")

    def test_deleting_rows_above_content_moves_its_metadata_with_the_row(self):
        with Shitty(columns=4, rows=6, save_lines=0) as terminal:
            terminal.write(
                put_rows(
                    b"A",
                    b"B",
                    b"C",
                    b"D",
                    b"\x1b]8;;https://example.test/e\x1b\\E\x1b]8;;\x1b\\",
                    b"F",
                )
            )

            terminal.write(b"\x1b[1;1H\x1b[3M")

            self.assertEqual(visible_lines(terminal), ("D", "E", "F", "", "", ""))
            self.assertEqual(terminal.hyperlink(0, 1), "https://example.test/e")

    def test_deleting_the_selected_row_invalidates_its_anchor(self):
        with Shitty(columns=4, rows=6, save_lines=0) as terminal:
            terminal.write(put_rows(b"A", b"B", b"C", b"D", b"E", b"F"))
            terminal.select_start(0, 1)
            terminal.select_update(1, 1)

            terminal.write(b"\x1b[1;1H\x1b[3M")

            self.assertEqual(terminal.snapshot().selection, (-1, -1, -1, -1))
            self.assertEqual(terminal.select_finish(), b"")

    def test_history_erase_moves_a_parked_viewport_back_to_active(self):
        with Shitty(columns=6, rows=3, save_lines=8) as terminal:
            terminal.write(numbered_lines(0, 8))
            terminal.wheel_up(3)
            self.assertNotEqual(terminal.snapshot().view_offset, 0)

            terminal.write(b"\x1b[3J")

            self.assertEqual(visible_lines(terminal), ("006", "007", "008"))
            self.assertEqual(terminal.snapshot().view_offset, 0)

    def test_pruning_a_viewport_anchor_clamps_it_to_the_new_history_top(self):
        with Shitty(columns=6, rows=3, save_lines=4) as terminal:
            terminal.write(numbered_lines(0, 6))
            terminal.wheel_up(100)
            self.assertEqual(visible_lines(terminal), ("000", "001", "002"))

            terminal.write(b"\r\n007")

            self.assertEqual(visible_lines(terminal), ("001", "002", "003"))
            self.assertEqual(terminal.scrollback_state(), (4, 7, 3, 0))

    def test_erasing_empty_history_keeps_the_viewport_active(self):
        with Shitty(columns=6, rows=3, save_lines=8) as terminal:
            terminal.write(put_rows(b"A", b"B", b"C"))
            terminal.wheel_up(100)

            terminal.write(b"\x1b[3J")

            self.assertEqual(visible_lines(terminal), ("A", "B", "C"))
            self.assertEqual(terminal.snapshot().view_offset, 0)

    def test_erasing_the_active_screen_preserves_its_configured_height(self):
        with Shitty(columns=6, rows=24, save_lines=0) as terminal:
            terminal.write(put_rows(b"A", b"B", b"C"))
            terminal.write(b"\x1b[2J")
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.rows, 24)
            self.assertEqual(tuple(line.rstrip() for line in snapshot.lines), ("",) * 24)

    def test_erasing_a_one_row_active_screen_clears_its_only_cell(self):
        with Shitty(columns=10, rows=1, save_lines=0) as terminal:
            terminal.write(b"A")
            terminal.write(b"\x1b[2J")

            self.assertEqual(visible_lines(terminal), ("",))
            self.assertEqual(terminal.snapshot().cell(0, 0).char, " ")

    def test_bounded_row_erase_shifts_only_the_selected_region(self):
        with Shitty(columns=4, rows=10, save_lines=0) as terminal:
            terminal.write(put_rows(*[bytes([ord("A") + row]) for row in range(10)]))
            terminal.select_start(0, 8)
            terminal.select_update(1, 8)

            terminal.write(b"\x1b[6;9r\x1b[3S\x1b[r")

            self.assertEqual(
                visible_lines(terminal),
                ("A", "B", "C", "D", "E", "I", "", "", "", "J"),
            )
            self.assertEqual(terminal.select_finish(), b"I")

    def test_bounded_erase_at_top_invalidates_a_pin_inside_erased_rows(self):
        with Shitty(columns=8, rows=6, save_lines=0) as terminal:
            terminal.write(put_rows(b"ABCDEF", b"B", b"C", b"D", b"E", b"F"))
            terminal.select_start(5, 0)
            terminal.select_update(6, 0)

            terminal.write(b"\x1b[1;4r\x1b[3S\x1b[r")

            self.assertEqual(visible_lines(terminal), ("D", "", "", "", "E", "F"))
            self.assertEqual(terminal.snapshot().selection, (-1, -1, -1, -1))
            self.assertEqual(terminal.select_finish(), b"")


if __name__ == "__main__":
    unittest.main()
