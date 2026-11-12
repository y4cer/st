# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Public adaptations of all xterm.js Buffer cases."""

import time
import unittest

from harness import Shitty


UPSTREAM_CASES = (
    "line storage capacity equals rows plus scrollback",
    "the initial scrolling-region bottom equals rows minus one",
    "filling the viewport creates one blank line per visible row",
    "a non-wrapped first row is one logical line",
    "a non-wrapped middle row is one logical line",
    "a non-wrapped last row is one logical line",
    "the first row includes its wrapped continuation",
    "a middle continuation includes the row above",
    "a middle row includes the continuation below",
    "a middle continuation includes the complete wrapped block",
    "the last row includes the wrapped row above",
    "a continuation can wrap upward to the first row",
    "a row can wrap downward to the last row",
    "width reduction resizes every blank viewport row",
    "width growth pads every blank viewport row",
    "height reduction trims blank rows from the end",
    "height reduction exposes backing rows when the cursor is above the tail",
    "height reduction without scrollback trims rows above the bottom cursor",
    "height growth appends blank rows to an empty buffer",
    "height growth reveals more backing rows above the viewport",
    "height growth keeps a viewport parked at the top",
    "old ConPTY growth preserves the viewport base and appends rows",
    "simultaneous row and column growth resizes every row",
    "width reduction does not wrap empty rows",
    "width and height reduction shrink every row",
    "a hard row wraps and unwraps",
    "ConPTY reflow is gated on build 21376",
    "modern ConPTY unwraps reflowed rows",
    "the cursor line reflows when that policy is enabled",
    "the cursor line does not reflow under the xterm.js default policy",
    "bounded scrollback discards the oldest chunks of a wrapped row",
    "width growth removes the correct chunks from successive wrapped rows",
    "combined grapheme data survives reflow",
    "line markers track their rows through shrink and growth",
    "line markers are disposed when their row heads are trimmed",
    "zero-space tails reflow correctly during width growth",
    "wide characters reflow correctly during width growth",
    "zero-space tails reflow correctly during width reduction",
    "wide characters reflow correctly during width reduction",
    "width growth compacts soft rows above an unfilled viewport",
    "width growth moves a bottom cursor while the viewport is full",
    "width growth follows the bottom with scrollback capacity remaining",
    "width growth preserves a viewport parked in scrollback",
    "width growth trims a full scrollback while following the bottom",
    "width growth preserves a parked viewport while scrollback is full",
    "width reduction moves a cursor in an unfilled viewport downward",
    "width reduction creates scrollback for a full viewport",
    "width reduction follows the bottom with scrollback capacity remaining",
    "width reduction preserves a viewport parked in scrollback",
    "width reduction trims a full scrollback while following the bottom",
    "width reduction preserves the visible anchor while scrollback is full",
    "a buffer without scrollback stays without scrollback across resize",
    "a line marker follows its row when the buffer head is trimmed",
    "a line marker disappears when its row is trimmed",
    "disposed marker state does not leak into reused rows",
    "an ASCII line can be extracted over an explicit range",
    "a range ending inside a wide cell includes the complete character",
    "a wide continuation cell contributes no extra character",
    "a single-cell supplementary character is extracted atomically",
    "a double-cell emoji is extracted atomically",
    "repeated line extraction remains stable across event-loop turns",
    "line extraction remains correct after clear and resize",
    "line contents survive deferred storage compaction after shrinking",
)


def select_line(terminal, column, row):
    terminal.select_start(column, row)
    terminal.select_extend(column, row, cycle=True)
    terminal.select_extend(column, row, cycle=True)
    return terminal.select_finish()


def put_at(row, text):
    return f"\x1b[{row + 1};1H".encode() + text


def write_reflow_fixture(terminal, cursor_row, with_scrollback=False):
    if with_scrollback:
        terminal.write(b"\r\n" * 19)
    terminal.write(
        b"\x1b[1;1Habcd\r\nefgh\r\nijkl"
        + f"\x1b[{cursor_row + 1};1H".encode()
    )


def select_range(terminal, start, end, row=0):
    terminal.select_start(start, row)
    terminal.select_update(end, row)
    return terminal.select_finish()


class XtermJsBufferTest(unittest.TestCase):
    def test_upstream_inventory_has_63_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 63)
        self.assertEqual(len(set(UPSTREAM_CASES)), 63)

    def test_line_storage_capacity_equals_rows_plus_scrollback(self):
        with Shitty(columns=4, rows=3, save_lines=2) as terminal:
            terminal.write(b"0\r\n1\r\n2\r\n3\r\n4\r\n5")
            self.assertEqual(terminal.scrollback_state(), (2, 5, 3, 2))
            terminal.wheel_up(100)
            self.assertEqual(
                tuple(line.rstrip() for line in terminal.snapshot().lines),
                ("1", "2", "3"),
            )

    def test_initial_scrolling_region_bottom_is_the_last_row(self):
        with Shitty(columns=4, rows=4, save_lines=2) as terminal:
            terminal.write(b"\x1b[4;1HA\r\nB")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[-2:], ["A   ", "B   "])
            self.assertEqual(terminal.scrollback_state()[0], 1)

    def test_fill_viewport_creates_blank_rows(self):
        with Shitty(columns=80, rows=24, save_lines=1000) as terminal:
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.columns, snapshot.rows), (80, 24))
            self.assertEqual(snapshot.lines, [" " * 80] * 24)
            self.assertEqual(terminal.scrollback_state(), (0, 24, 24, 0))

    def test_nonwrapped_first_row_is_one_logical_line(self):
        with Shitty(columns=8, rows=24) as terminal:
            terminal.write(put_at(0, b"first"))
            self.assertEqual(select_line(terminal, 1, 0), b"first")

    def test_nonwrapped_middle_row_is_one_logical_line(self):
        with Shitty(columns=8, rows=24) as terminal:
            terminal.write(put_at(12, b"middle"))
            self.assertEqual(select_line(terminal, 1, 12), b"middle")

    def test_nonwrapped_last_row_is_one_logical_line(self):
        with Shitty(columns=8, rows=24) as terminal:
            terminal.write(put_at(23, b"last"))
            self.assertEqual(select_line(terminal, 1, 23), b"last")

    def test_first_row_includes_its_wrapped_continuation(self):
        with Shitty(columns=4, rows=24) as terminal:
            terminal.write(put_at(0, b"ABCDEFGH"))
            self.assertEqual(select_line(terminal, 1, 0), b"ABCDEFGH")

    def test_middle_continuation_includes_the_row_above(self):
        with Shitty(columns=4, rows=24) as terminal:
            terminal.write(put_at(11, b"ABCDEFGH"))
            self.assertEqual(select_line(terminal, 1, 12), b"ABCDEFGH")

    def test_middle_row_includes_the_continuation_below(self):
        with Shitty(columns=4, rows=24) as terminal:
            terminal.write(put_at(12, b"ABCDEFGH"))
            self.assertEqual(select_line(terminal, 1, 12), b"ABCDEFGH")

    def test_middle_continuation_includes_the_complete_wrapped_block(self):
        with Shitty(columns=4, rows=24) as terminal:
            terminal.write(put_at(10, b"ABCDEFGHIJKLMNOPQRST"))
            self.assertEqual(
                select_line(terminal, 1, 12),
                b"ABCDEFGHIJKLMNOPQRST",
            )

    def test_last_row_includes_the_wrapped_row_above(self):
        with Shitty(columns=4, rows=24) as terminal:
            terminal.write(put_at(22, b"ABCDEFGH"))
            self.assertEqual(select_line(terminal, 1, 23), b"ABCDEFGH")

    def test_continuation_can_wrap_upward_to_the_first_row(self):
        with Shitty(columns=4, rows=24) as terminal:
            terminal.write(put_at(0, b"ABCDEFGH"))
            self.assertEqual(select_line(terminal, 1, 1), b"ABCDEFGH")

    def test_row_can_wrap_downward_to_the_last_row(self):
        with Shitty(columns=4, rows=24) as terminal:
            terminal.write(put_at(22, b"ABCDEFGH"))
            self.assertEqual(select_line(terminal, 1, 22), b"ABCDEFGH")

    def test_width_reduction_resizes_every_blank_viewport_row(self):
        with Shitty(columns=80, rows=24) as terminal:
            terminal.resize(40, 24)
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.columns, snapshot.rows), (40, 24))
            self.assertEqual(snapshot.lines, [" " * 40] * 24)

    def test_width_growth_pads_every_blank_viewport_row(self):
        with Shitty(columns=80, rows=24) as terminal:
            terminal.resize(90, 24)
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.columns, snapshot.rows), (90, 24))
            self.assertEqual(snapshot.lines, [" " * 90] * 24)

    def test_height_reduction_trims_blank_rows_from_the_end(self):
        with Shitty(columns=80, rows=24) as terminal:
            terminal.resize(80, 14)
            self.assertEqual(terminal.scrollback_state(), (0, 14, 14, 0))
            self.assertEqual(terminal.snapshot().lines, [" " * 80] * 14)

    def test_height_reduction_exposes_backing_rows_above_the_cursor(self):
        with Shitty(columns=80, rows=24, save_lines=1000) as terminal:
            terminal.write(b"\x1b[19;1H")
            terminal.resize(80, 14)
            snapshot = terminal.snapshot()
            self.assertEqual(terminal.scrollback_state(), (5, 19, 14, 5))
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 13))

    def test_height_reduction_without_scrollback_trims_above_bottom_cursor(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(put_at(5, b"a") + put_at(23, b"b"))
            terminal.resize(80, 19)
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0][0], "a")
            self.assertEqual(snapshot.lines[18][0], "b")
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 18))

    def test_height_growth_appends_blank_rows_to_an_empty_buffer(self):
        with Shitty(columns=80, rows=24) as terminal:
            terminal.resize(80, 34)
            self.assertEqual(terminal.scrollback_state(), (0, 34, 34, 0))
            self.assertEqual(terminal.snapshot().lines, [" " * 80] * 34)

    def test_height_growth_reveals_more_backing_rows_above_the_viewport(self):
        with Shitty(columns=80, rows=24, save_lines=1000) as terminal:
            terminal.write(b"\r\n" * 33)
            self.assertEqual(terminal.scrollback_state(), (10, 34, 24, 10))
            terminal.resize(80, 29)
            self.assertEqual(terminal.scrollback_state(), (5, 34, 29, 5))

    def test_height_growth_keeps_a_viewport_parked_at_the_top(self):
        with Shitty(columns=80, rows=24, save_lines=1000) as terminal:
            terminal.write(b"\r\n" * 33)
            terminal.wheel_up(100)
            self.assertEqual(terminal.scrollback_state(), (10, 34, 24, 0))

            terminal.resize(80, 29)

            self.assertEqual(terminal.scrollback_state(), (5, 34, 29, 0))

    # This is an xterm.js compatibility mode for old Windows ConPTY builds.
    # Shitty has no backend-specific grid policy and follows ordinary reflow.
    @unittest.expectedFailure
    def test_old_conpty_growth_preserves_the_base_and_appends_rows(self):
        with Shitty(columns=80, rows=24, save_lines=1000) as terminal:
            terminal.write(b"\r\n" * 33)
            self.assertEqual(terminal.scrollback_state(), (10, 34, 24, 10))

            terminal.resize(80, 29)

            self.assertEqual(terminal.scrollback_state(), (10, 39, 29, 10))

    def test_simultaneous_row_and_column_growth_resizes_every_row(self):
        with Shitty(columns=80, rows=24, save_lines=1000) as terminal:
            terminal.resize(85, 29)
            snapshot = terminal.snapshot()

            self.assertEqual(terminal.scrollback_state(), (0, 29, 29, 0))
            self.assertEqual(snapshot.lines, [" " * 85] * 29)

    def test_width_reduction_does_not_wrap_empty_rows(self):
        with Shitty(columns=80, rows=24, save_lines=1000) as terminal:
            terminal.resize(75, 24)
            snapshot = terminal.snapshot()

            self.assertEqual(terminal.scrollback_state(), (0, 24, 24, 0))
            self.assertEqual(snapshot.lines, [" " * 75] * 24)
            self.assertFalse(any(cell.wrapped for cell in snapshot.cells))

    def test_width_and_height_reduction_shrink_every_row(self):
        with Shitty(columns=80, rows=24, save_lines=1000) as terminal:
            terminal.resize(5, 10)
            snapshot = terminal.snapshot()

            self.assertEqual(terminal.scrollback_state(), (0, 10, 10, 0))
            self.assertEqual(snapshot.lines, [" " * 5] * 10)

    def test_a_hard_row_wraps_and_unwraps(self):
        with Shitty(columns=5, rows=10, save_lines=1000) as terminal:
            terminal.write(b"abcde\x1b[2;1H")

            terminal.resize(1, 10)
            self.assertEqual(
                terminal.all_text(),
                ("a", "b", "c", "d", "e", "", "", "", "", ""),
            )

            terminal.resize(5, 10)
            self.assertEqual(
                terminal.all_text(),
                ("abcde", "", "", "", "", "", "", "", "", ""),
            )

    # xterm.js exposes the ConPTY build as a buffer policy input. Shitty's
    # PTY and terminal are intentionally independent, so both runs use the
    # same generic reflow policy and cannot reproduce the legacy half.
    @unittest.expectedFailure
    def test_conpty_reflow_is_gated_on_build_21376(self):
        def shrink():
            with Shitty(columns=5, rows=10, save_lines=1000) as terminal:
                terminal.write(b"abcde\x1b[2;1H")
                terminal.resize(1, 10)
                return terminal.all_text()[1]

        legacy_build = shrink()
        modern_build = shrink()
        self.assertEqual((legacy_build, modern_build), ("", "b"))

    def test_modern_conpty_unwraps_reflowed_rows(self):
        with Shitty(columns=5, rows=10, save_lines=1000) as terminal:
            terminal.write(b"abcde\x1b[2;1H")
            terminal.resize(1, 10)
            terminal.resize(5, 10)

            self.assertEqual(terminal.all_text()[:2], ("abcde", ""))

    def test_cursor_line_reflows_when_the_policy_is_enabled(self):
        with Shitty(columns=5, rows=10, save_lines=1000) as terminal:
            terminal.write(b"abcde")
            terminal.resize(1, 10)
            terminal.write(b"\x1b[3;1H")

            terminal.resize(5, 10)

            self.assertEqual(terminal.all_text()[0], "abcde")

    # xterm.js defaults reflowCursorLine to false. Shitty follows the main
    # terminal consensus and keeps reflow independent of cursor placement.
    @unittest.expectedFailure
    def test_xtermjs_default_policy_does_not_reflow_the_cursor_line(self):
        with Shitty(columns=5, rows=10, save_lines=1000) as terminal:
            terminal.write(b"abcde")
            terminal.resize(1, 10)
            terminal.write(b"\x1b[3;1H")

            terminal.resize(5, 10)

            self.assertNotEqual(terminal.all_text()[0], "abcde")

    def test_bounded_scrollback_discards_oldest_wrapped_chunks(self):
        with Shitty(columns=10, rows=5, save_lines=1) as terminal:
            terminal.write(b"\x1b[4;1Habcdefghij\x1b[5;1H")

            terminal.resize(2, 5)
            self.assertEqual(terminal.scrollback_state(), (1, 6, 5, 1))
            self.assertEqual(
                terminal.all_text(),
                ("ab", "cd", "ef", "gh", "ij", ""),
            )

            terminal.resize(1, 5)
            self.assertEqual(terminal.scrollback_state(), (1, 6, 5, 1))
            self.assertEqual(
                terminal.all_text(),
                ("f", "g", "h", "i", "j", ""),
            )

            terminal.resize(10, 5)
            snapshot = terminal.snapshot()
            self.assertEqual(terminal.scrollback_state(), (0, 5, 5, 0))
            self.assertEqual(terminal.all_text(), ("fghij", "", "", "", ""))
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 1))

    def test_growth_removes_correct_chunks_from_successive_wrapped_rows(self):
        with Shitty(columns=10, rows=10, save_lines=1000) as terminal:
            terminal.write(b"abcdefghij\r\n0123456789\x1b[3;1H")

            terminal.resize(2, 10)
            self.assertEqual(terminal.scrollback_state(), (1, 11, 10, 1))
            self.assertEqual(
                terminal.all_text(),
                ("ab", "cd", "ef", "gh", "ij", "01", "23", "45", "67", "89", ""),
            )

            terminal.resize(10, 10)
            self.assertEqual(terminal.scrollback_state(), (0, 10, 10, 0))
            self.assertEqual(
                terminal.all_text(),
                ("abcdefghij", "0123456789", "", "", "", "", "", "", "", ""),
            )

    def test_combined_grapheme_data_survives_reflow(self):
        combined = "c\N{COMBINING ACUTE ACCENT}"
        with Shitty(columns=4, rows=3, save_lines=1000) as terminal:
            terminal.write(("ab" + combined + "d").encode() + b"\x1b[3;1H")

            terminal.resize(2, 3)

            self.assertEqual(terminal.all_text()[:2], ("ab", combined + "d"))

    def test_line_markers_track_rows_through_shrink_and_growth(self):
        marker = b"\x1b]133;A\x1b\\"
        with Shitty(columns=10, rows=16, save_lines=1000) as terminal:
            terminal.write(
                marker + b"abcdefghij\r\n"
                + marker + b"0123456789\r\n"
                + marker + b"klmnopqrst\x1b[4;1H"
            )
            self.assertEqual(tuple(terminal.row_semantic(row) for row in range(3)), (1, 1, 1))

            terminal.resize(2, 16)
            self.assertEqual(
                terminal.all_text()[:15],
                (
                    "ab", "cd", "ef", "gh", "ij",
                    "01", "23", "45", "67", "89",
                    "kl", "mn", "op", "qr", "st",
                ),
            )
            self.assertEqual(
                tuple(terminal.row_semantic(row) for row in range(15)),
                (1, 2, 2, 2, 2, 1, 2, 2, 2, 2, 1, 2, 2, 2, 2),
            )

            terminal.resize(10, 16)
            self.assertEqual(terminal.all_text()[:3], ("abcdefghij", "0123456789", "klmnopqrst"))
            self.assertEqual(tuple(terminal.row_semantic(row) for row in range(3)), (1, 1, 1))

    def test_line_markers_are_disposed_when_heads_are_trimmed(self):
        marker = b"\x1b]133;A\x1b\\"
        with Shitty(columns=10, rows=11, save_lines=1) as terminal:
            terminal.write(
                marker + b"abcdefghij\r\n"
                + marker + b"0123456789\r\n"
                + marker + b"klmnopqrst\x1b[11;1H\x1b[4;1H"
            )

            terminal.resize(2, 11)
            self.assertEqual(
                terminal.all_text()[:11],
                ("ij", "01", "23", "45", "67", "89", "kl", "mn", "op", "qr", "st"),
            )
            self.assertEqual(terminal.row_semantic(-1), 2)
            self.assertEqual(terminal.row_semantic(0), 1)
            self.assertEqual(terminal.row_semantic(5), 1)

            terminal.resize(10, 11)
            self.assertEqual(terminal.all_text()[:3], ("ij", "0123456789", "klmnopqrst"))
            self.assertEqual(
                tuple(terminal.row_semantic(row) for row in range(3)),
                (2, 1, 1),
            )

    def test_zero_space_tails_reflow_during_width_growth(self):
        with Shitty(columns=4, rows=10, save_lines=1000) as terminal:
            terminal.write(b"ab  cd\x1b[3;1H")

            terminal.resize(5, 10)
            self.assertEqual(terminal.all_text()[:2], ("ab  c", "d"))

            terminal.resize(6, 10)
            self.assertEqual(terminal.all_text()[:2], ("ab  cd", ""))

    def test_wide_characters_reflow_during_width_growth(self):
        payload = "汉语" * 6
        with Shitty(columns=12, rows=10, save_lines=1000) as terminal:
            terminal.write(payload.encode() + b"\x1b[3;1H")

            terminal.resize(13, 10)
            self.assertEqual(terminal.all_text()[:2], ("汉语汉语汉语", "汉语汉语汉语"))

            terminal.resize(14, 10)
            self.assertEqual(terminal.all_text()[:2], ("汉语汉语汉语汉", "语汉语汉语"))

    def test_zero_space_tails_reflow_during_width_reduction(self):
        with Shitty(columns=4, rows=10, save_lines=1000) as terminal:
            terminal.write(b"ab  cd\x1b[3;1H")

            terminal.resize(3, 10)
            snapshot = terminal.snapshot()
            self.assertEqual(terminal.all_text()[:2], ("ab ", " cd"))
            self.assertEqual(snapshot.cursor_y, 2)

            terminal.resize(2, 10)
            snapshot = terminal.snapshot()
            self.assertEqual(terminal.all_text()[:3], ("ab", "  ", "cd"))
            self.assertEqual(snapshot.cursor_y, 3)

    def test_wide_characters_reflow_during_width_reduction(self):
        payload = "汉语" * 6
        expected = {
            11: ("汉语汉语汉", "语汉语汉语", "汉语"),
            10: ("汉语汉语汉", "语汉语汉语", "汉语"),
            9: ("汉语汉语", "汉语汉语", "汉语汉语"),
            8: ("汉语汉语", "汉语汉语", "汉语汉语"),
            7: ("汉语汉", "语汉语", "汉语汉", "语汉语"),
            6: ("汉语汉", "语汉语", "汉语汉", "语汉语"),
        }
        with Shitty(columns=12, rows=10, save_lines=1000) as terminal:
            terminal.write(payload.encode() + b"\x1b[3;1H")

            for columns, lines in expected.items():
                with self.subTest(columns=columns):
                    terminal.resize(columns, 10)
                    self.assertEqual(terminal.all_text()[:len(lines)], lines)

    def test_growth_compacts_soft_rows_above_an_unfilled_viewport(self):
        with Shitty(columns=2, rows=10, save_lines=1000) as terminal:
            terminal.write(b"abcd\r\nefgh\r\nijkl\x1b[7;1H")

            terminal.resize(4, 10)
            snapshot = terminal.snapshot()

            self.assertEqual(terminal.scrollback_state(), (0, 10, 10, 0))
            self.assertEqual(
                terminal.all_text(),
                ("abcd", "efgh", "ijkl", "", "", "", "", "", "", ""),
            )
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 3))
            self.assertFalse(any(cell.wrapped for cell in snapshot.cells))

    def test_growth_moves_a_bottom_cursor_in_a_full_viewport(self):
        with Shitty(columns=2, rows=10, save_lines=1000) as terminal:
            write_reflow_fixture(terminal, 9)

            terminal.resize(4, 10)
            snapshot = terminal.snapshot()

            self.assertEqual(terminal.scrollback_state(), (0, 10, 10, 0))
            self.assertEqual(terminal.all_text()[:3], ("abcd", "efgh", "ijkl"))
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 6))

    def test_growth_follows_bottom_with_scrollback_capacity_remaining(self):
        with Shitty(columns=2, rows=10, save_lines=1000) as terminal:
            write_reflow_fixture(terminal, 9, with_scrollback=True)

            terminal.resize(4, 10)

            self.assertEqual(terminal.scrollback_state(), (7, 17, 10, 7))
            self.assertEqual(terminal.all_text()[10:13], ("abcd", "efgh", "ijkl"))

    def test_growth_preserves_a_viewport_parked_in_scrollback(self):
        with Shitty(columns=2, rows=10, save_lines=1000) as terminal:
            write_reflow_fixture(terminal, 9, with_scrollback=True)
            terminal.wheel_up(5)

            terminal.resize(4, 10)

            self.assertEqual(terminal.scrollback_state(), (7, 17, 10, 5))
            self.assertEqual(terminal.all_text()[10:13], ("abcd", "efgh", "ijkl"))

    def test_growth_trims_full_scrollback_while_following_bottom(self):
        with Shitty(columns=2, rows=10, save_lines=10) as terminal:
            write_reflow_fixture(terminal, 9, with_scrollback=True)

            terminal.resize(4, 10)

            self.assertEqual(terminal.scrollback_state(), (7, 17, 10, 7))
            self.assertEqual(terminal.all_text()[10:13], ("abcd", "efgh", "ijkl"))

    def test_growth_preserves_parked_viewport_while_scrollback_is_full(self):
        with Shitty(columns=2, rows=10, save_lines=10) as terminal:
            write_reflow_fixture(terminal, 9, with_scrollback=True)
            terminal.wheel_up(5)

            terminal.resize(4, 10)

            self.assertEqual(terminal.scrollback_state(), (7, 17, 10, 5))
            self.assertEqual(terminal.all_text()[10:13], ("abcd", "efgh", "ijkl"))

    def test_reduction_moves_a_cursor_in_an_unfilled_viewport_downward(self):
        with Shitty(columns=4, rows=10, save_lines=1000) as terminal:
            write_reflow_fixture(terminal, 3)

            terminal.resize(2, 10)
            snapshot = terminal.snapshot()

            self.assertEqual(terminal.scrollback_state(), (0, 10, 10, 0))
            self.assertEqual(
                terminal.all_text()[:6],
                ("ab", "cd", "ef", "gh", "ij", "kl"),
            )
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 6))

    def test_reduction_creates_scrollback_for_a_full_viewport(self):
        with Shitty(columns=4, rows=10, save_lines=1000) as terminal:
            write_reflow_fixture(terminal, 9)

            terminal.resize(2, 10)

            self.assertEqual(terminal.scrollback_state(), (3, 13, 10, 3))
            self.assertEqual(
                terminal.all_text()[:6],
                ("ab", "cd", "ef", "gh", "ij", "kl"),
            )

    def test_reduction_follows_bottom_with_scrollback_capacity_remaining(self):
        with Shitty(columns=4, rows=10, save_lines=1000) as terminal:
            write_reflow_fixture(terminal, 9, with_scrollback=True)

            terminal.resize(2, 10)

            self.assertEqual(terminal.scrollback_state(), (13, 23, 10, 13))
            self.assertEqual(
                terminal.all_text()[10:16],
                ("ab", "cd", "ef", "gh", "ij", "kl"),
            )

    def test_reduction_preserves_a_viewport_parked_in_scrollback(self):
        with Shitty(columns=4, rows=10, save_lines=1000) as terminal:
            write_reflow_fixture(terminal, 9, with_scrollback=True)
            terminal.wheel_up(5)

            terminal.resize(2, 10)

            self.assertEqual(terminal.scrollback_state(), (13, 23, 10, 5))
            self.assertEqual(
                terminal.all_text()[10:16],
                ("ab", "cd", "ef", "gh", "ij", "kl"),
            )

    def test_reduction_trims_full_scrollback_while_following_bottom(self):
        with Shitty(columns=4, rows=10, save_lines=10) as terminal:
            write_reflow_fixture(terminal, 9, with_scrollback=True)

            terminal.resize(2, 10)

            self.assertEqual(terminal.scrollback_state(), (10, 20, 10, 10))
            self.assertEqual(
                terminal.all_text()[7:13],
                ("ab", "cd", "ef", "gh", "ij", "kl"),
            )

    def test_reduction_preserves_visible_anchor_while_scrollback_is_full(self):
        with Shitty(columns=4, rows=10, save_lines=10) as terminal:
            write_reflow_fixture(terminal, 9, with_scrollback=True)
            terminal.wheel_up(5)
            before = terminal.snapshot().lines

            terminal.resize(2, 10)
            after = terminal.snapshot().lines

            self.assertEqual(terminal.scrollback_state(), (10, 20, 10, 2))
            self.assertEqual(before[:5], [" " * 4] * 5)
            self.assertEqual(after[:5], [" " * 2] * 5)
            self.assertEqual(
                terminal.all_text()[7:13],
                ("ab", "cd", "ef", "gh", "ij", "kl"),
            )

    def test_no_scrollback_buffer_stays_without_scrollback_across_resize(self):
        with Shitty(columns=8, rows=6, save_lines=1000) as terminal:
            terminal.write(b"\x1b[?1049h")
            self.assertEqual(terminal.scrollback_state(), (0, 6, 6, 0))

            terminal.resize(8, 12)
            self.assertEqual(terminal.scrollback_state(), (0, 12, 12, 0))

            terminal.resize(8, 3)
            self.assertEqual(terminal.scrollback_state(), (0, 3, 3, 0))

    def test_line_marker_follows_its_row_when_buffer_head_is_trimmed(self):
        marker = b"\x1b]133;A\x1b\\"
        with Shitty(columns=8, rows=3, save_lines=2) as terminal:
            terminal.write(b"\x1b[3;1H" + marker + b"tail")
            self.assertEqual(terminal.row_semantic(2), 1)

            terminal.write(b"\r\nnext")

            self.assertEqual(terminal.scrollback_state(), (1, 4, 3, 1))
            self.assertEqual(terminal.row_semantic(1), 1)
            self.assertEqual(terminal.all_text(), ("", "", "tail", "next"))

    def test_line_marker_disappears_when_its_row_is_trimmed(self):
        marker = b"\x1b]133;A\x1b\\"
        with Shitty(columns=8, rows=3, save_lines=0) as terminal:
            terminal.write(marker + b"old\x1b]133;D\x1b\\")
            self.assertEqual(terminal.row_semantic(0), 1)

            terminal.write(b"\r\n1\r\n2\r\n3")

            self.assertNotIn("old", terminal.all_text())
            self.assertNotIn(1, tuple(terminal.row_semantic(row) for row in range(3)))

    def test_disposed_marker_state_does_not_leak_into_reused_rows(self):
        marker = b"\x1b]133;A\x1b\\"
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.write(marker + b"old\x1b]133;D\x1b\\\r\nnew\r\ntail")
            self.assertNotIn("old", terminal.all_text())

            terminal.write(b"\x1b[1;1Hfresh")

            self.assertEqual(terminal.row_semantic(0), 0)
            self.assertEqual(terminal.all_text(), ("fresh", "tail"))

    def test_ascii_line_can_be_extracted_over_an_explicit_range(self):
        with Shitty(columns=4, rows=2) as terminal:
            terminal.write(b"abcd")
            self.assertEqual(select_range(terminal, 0, 2), b"ab")

    def test_range_ending_inside_wide_cell_includes_complete_character(self):
        with Shitty(columns=3, rows=2) as terminal:
            terminal.write("語a".encode())
            self.assertEqual(select_range(terminal, 0, 1), "語".encode())

    def test_wide_continuation_cell_contributes_no_extra_character(self):
        with Shitty(columns=3, rows=2) as terminal:
            terminal.write("語a".encode())
            self.assertEqual(select_range(terminal, 0, 1), "語".encode())
            self.assertEqual(select_range(terminal, 0, 2), "語".encode())
            self.assertEqual(select_range(terminal, 0, 3), "語a".encode())

    def test_single_cell_supplementary_character_is_extracted_atomically(self):
        text = "𝄞a"
        with Shitty(columns=2, rows=2) as terminal:
            terminal.write(text.encode())
            self.assertEqual(select_range(terminal, 0, 1), "𝄞".encode())
            self.assertEqual(select_range(terminal, 0, 2), text.encode())

    def test_double_cell_emoji_is_extracted_atomically(self):
        text = "😁a"
        with Shitty(columns=3, rows=2) as terminal:
            terminal.write(text.encode())
            self.assertEqual(select_range(terminal, 0, 1), "😁".encode())
            self.assertEqual(select_range(terminal, 0, 2), "😁".encode())
            self.assertEqual(select_range(terminal, 0, 3), text.encode())

    def test_repeated_line_extraction_is_stable_across_event_loop_turns(self):
        with Shitty(columns=4, rows=2) as terminal:
            terminal.write(b"a\x1b[2;1Hb")
            expected = ("a", "b")

            for _ in range(3):
                self.assertEqual(terminal.all_text(), expected)
                terminal.pump()

    def test_line_extraction_remains_correct_after_clear_and_resize(self):
        with Shitty(columns=4, rows=2) as terminal:
            terminal.write(b"a")
            self.assertEqual(terminal.all_text(), ("a", ""))

            terminal.hard_reset()
            terminal.write(b"b")
            self.assertEqual(terminal.all_text(), ("b", ""))

            terminal.resize(3, 2)
            self.assertEqual(terminal.all_text(), ("b", ""))

    def test_line_contents_survive_deferred_storage_compaction_after_shrinking(self):
        with Shitty(columns=80, rows=4) as terminal:
            terminal.write(b"abcdefghijklmnopqrstuvwxyz")

            terminal.resize(39, 4)
            immediate = terminal.all_text()
            time.sleep(0.05)
            terminal.pump()

            self.assertEqual(terminal.all_text(), immediate)
            self.assertEqual(immediate[0], "abcdefghijklmnopqrstuvwxyz")


if __name__ == "__main__":
    unittest.main()
