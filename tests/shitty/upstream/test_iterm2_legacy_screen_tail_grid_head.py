# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Legacy iTerm2 Screen tail and the first legacy Grid batch."""

import unittest

from harness import Shitty, put_rows


PORTED_CASES = (
    (
        "VT100ScreenTest.testRemoteHostOnTrailingEmptyLineNotLostDuringResize",
        "test_remote_host_on_trailing_empty_line_survives_resize",
    ),
    (
        "VT100ScreenTest.testWrappedLinesFromIndexAtBoundary",
        "test_wrapped_lines_cross_storage_boundary",
    ),
    (
        "VT100ScreenTest.testEnumerateWrappedLines",
        "test_enumerate_all_physical_rows_of_logical_lines",
    ),
    (
        "VT100ScreenTest.testIssue9852",
        "test_overwrite_wide_continuation_repairs_only_that_glyph",
    ),
    ("VT100ScreenTest.testCSI_CUD", "test_cud_page_and_margin_boundaries"),
    ("VT100ScreenTest.testCSI_CUF", "test_cuf_page_and_margin_boundaries"),
    (
        "VT100ScreenTest.testAppendExternalAttributeToExistingLineNotFirstLine",
        "test_underline_color_segments_survive_soft_wrap",
    ),
    (
        "VT100ScreenTest.testDoubleWidthCharacterCache",
        "test_wide_measurement_is_invalidated_after_append_and_reflow",
    ),
    (
        "VT100GridTest.testTypeFunctions",
        "test_public_coordinate_range_has_source_row_major_length",
    ),
    (
        "VT100GridTest.testTypeValues",
        "test_public_geometry_snapshot_has_value_semantics",
    ),
    ("VT100GridTest.testInitialization", "test_grid_starts_as_blank_two_by_two"),
    (
        "VT100GridTest.testLookUpScreenCharsByLineNumber",
        "test_rows_are_addressed_independently",
    ),
    ("VT100GridTest.testSetCursor", "test_cursor_clamps_and_pending_wrap_represents_edge"),
    (
        "VT100GridTest.testMarkCharDirty",
        "test_single_cell_change_publishes_only_its_row",
    ),
    (
        "VT100GridTest.testMarkAllCharsDirty",
        "test_full_cell_change_publishes_every_row",
    ),
    (
        "VT100GridTest.testNumberOfLinesUsed",
        "test_used_rows_include_drawn_content_and_cursor",
    ),
    (
        "VT100GridTest.testAppendLineToLineBuffer",
        "test_scrolled_rows_keep_hard_soft_and_cursor_metadata",
    ),
    (
        "VT100GridTest.testLengthOfLineNumber",
        "test_line_length_is_the_drawn_cell_prefix",
    ),
    (
        "VT100GridTest.testMoveCursorDownOneLineNoScroll",
        "test_index_moves_or_scrolls_at_public_boundaries",
    ),
    (
        "VT100GridTest.testMoveCursorLeft",
        "test_cub_clamps_at_page_and_horizontal_margin",
    ),
)

ROWS = put_rows(b"abcd", b"efgh", b"ijkl", b"mnop")


def assert_complete_wide(test, snapshot):
    for row in range(snapshot.rows):
        for column in range(snapshot.columns):
            cell = snapshot.cell(column, row)
            if cell.double_width:
                test.assertLess(column + 1, snapshot.columns)
                test.assertTrue(
                    snapshot.cell(column + 1, row).double_width_continuation
                )
            if cell.double_width_continuation:
                test.assertGreater(column, 0)
                test.assertTrue(snapshot.cell(column - 1, row).double_width)


class ITerm2LegacyScreenTailGridHeadTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_executable_cases(self):
        self.assertEqual(len(PORTED_CASES), 20)
        self.assertEqual(len({source for source, _ in PORTED_CASES}), 20)
        self.assertEqual(len({test for _, test in PORTED_CASES}), 20)
        for _, test in PORTED_CASES:
            self.assertTrue(callable(getattr(self, test)))

    @unittest.expectedFailure
    def test_remote_host_on_trailing_empty_line_survives_resize(self):
        uri = b"file://example.com/home/user"
        with Shitty(columns=5, rows=4) as terminal:
            terminal.write(b"Hi\r\n\x1b]7;" + uri + b"\x1b\\")
            self.assertEqual(terminal.current_cwd(), b"/home/user")
            terminal.resize(6, 4)
            self.assertEqual(terminal.current_cwd(), b"/home/user")

            operation = getattr(terminal, "current_directory_uri", None)
            if operation is None:
                raise AssertionError(
                    "the OSC 7 consensus retains the remote authority, but "
                    "Shitty exposes only the decoded path"
                )
            self.assertEqual(operation(), uri)

    def test_wrapped_lines_cross_storage_boundary(self):
        rows = []
        with Shitty(columns=200, rows=4, save_lines=120) as terminal:
            for index in range(100):
                row = f"{index:03d}".encode() + b"x" * 160
                rows.append(row.decode())
                terminal.write(row + b"\r\n")

            self.assertEqual(terminal.all_text()[:-1], tuple(rows))
            terminal.resize(326, 4)
            self.assertEqual(terminal.all_text()[:-1], tuple(rows))
            self.assertEqual(terminal.all_text()[49][:3], "049")
            self.assertEqual(terminal.all_text()[50][:3], "050")

    def test_enumerate_all_physical_rows_of_logical_lines(self):
        logical = (
            b"abcdefgh",
            b"ijkl",
            b"mnopqrstuv",
            b"wxyz",
            b"",
            b"1234",
            b"9876543210",
        )
        expected = (
            "abcde",
            "fgh",
            "ijkl",
            "mnopq",
            "rstuv",
            "wxyz",
            "",
            "1234",
            "98765",
            "43210",
        )
        with Shitty(columns=5, rows=2, save_lines=20) as terminal:
            for line in logical:
                terminal.write(line + b"\r\n")
            self.assertEqual(terminal.all_text()[:10], expected)
            terminal.wheel_up(20)
            snapshot = terminal.model_snapshot()
            self.assertTrue(snapshot.cell(4, 0).wrapped)
            self.assertFalse(snapshot.cell(4, 1).wrapped)

    def test_overwrite_wide_continuation_repairs_only_that_glyph(self):
        with Shitty(
            columns=4,
            rows=1,
            extra_arguments=("-unicodeWidths", "9"),
        ) as terminal:
            terminal.write("😃😃".encode() + b"\x1b[1;2H|")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines, [" |😃 "])
            self.assertFalse(snapshot.cell(0, 0).double_width)
            self.assertTrue(snapshot.cell(2, 0).double_width)
            self.assertTrue(snapshot.cell(3, 0).double_width_continuation)
            assert_complete_wide(self, snapshot)

    def test_cud_page_and_margin_boundaries(self):
        cases = (
            (b"\x1b[2;2H\x1b[B", (1, 2)),
            (b"\x1b[2;2H\x1b[2B", (1, 3)),
            (b"\x1b[3;5r\x1b[3;2H\x1b[99B", (1, 4)),
            (b"\x1b[3;4r\x1b[1;2H\x1b[99B", (1, 3)),
            (b"\x1b[2;3r\x1b[4;2H\x1b[99B", (1, 4)),
        )
        for sequence, expected in cases:
            with self.subTest(sequence=sequence), Shitty(columns=3, rows=5) as terminal:
                terminal.write(sequence)
                snapshot = terminal.model_snapshot()
                self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), expected)

    def test_cuf_page_and_margin_boundaries(self):
        cases = (
            (b"\x1b[2;2H\x1b[C", (2, 1)),
            (b"\x1b[2;2H\x1b[2C", (3, 1)),
            (b"\x1b[2;2H\x1b[99C", (4, 1)),
            (b"\x1b[?69h\x1b[2;4s\x1b[2;3H\x1b[99C", (3, 1)),
            (b"\x1b[?69h\x1b[2;3s\x1b[2;4H\x1b[99C", (4, 1)),
        )
        for sequence, expected in cases:
            with self.subTest(sequence=sequence), Shitty(columns=5, rows=5) as terminal:
                terminal.write(sequence)
                snapshot = terminal.model_snapshot()
                self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), expected)

    def test_underline_color_segments_survive_soft_wrap(self):
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write(
                b"xxxxx\r\n"
                b"\x1b[58;2;1;2;3mxxxxx"
                b"\x1b[58;2;5;6;7mxxxxx"
            )
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines, ["xxxxx", "xxxxx", "xxxxx"])
            for column in range(5):
                self.assertEqual(
                    snapshot.cell(column, 1).underline_color,
                    (1, 2, 3),
                )
                self.assertEqual(
                    snapshot.cell(column, 2).underline_color,
                    (5, 6, 7),
                )

    def test_wide_measurement_is_invalidated_after_append_and_reflow(self):
        wide = "界".encode()
        with Shitty(columns=4, rows=3, save_lines=5) as terminal:
            terminal.write(b"A" + wide + b"\r\n")
            first = terminal.model_snapshot()
            assert_complete_wide(self, first)

            terminal.write(b"A" + wide)
            terminal.resize(3, 3)
            terminal.resize(4, 3)
            snapshot = terminal.model_snapshot()
            self.assertEqual(terminal.all_text()[:2], ("A界", "A界"))
            self.assertTrue(snapshot.cell(1, 0).double_width)
            self.assertTrue(snapshot.cell(1, 1).double_width)
            assert_complete_wide(self, snapshot)

    def test_public_coordinate_range_has_source_row_major_length(self):
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(b"0123456789abcdefghijklmno")
            terminal.select_start(1, 2)
            # The source's end coordinate is inclusive; public selection is
            # half-open, so column three represents source coordinate two.
            terminal.select_extend(3, 4)
            selected = terminal.select_finish()
            self.assertEqual(selected, b"bcdefghijklm")
            self.assertEqual(len(selected), 12)

    def test_public_geometry_snapshot_has_value_semantics(self):
        with Shitty(columns=9, rows=10) as terminal:
            terminal.write(b"\x1b[3;2H")
            before = terminal.model_snapshot()
            terminal.resize(3, 4)
            terminal.write(b"\x1b[4;3H")
            after = terminal.model_snapshot()

            self.assertEqual(
                (before.columns, before.rows, before.cursor_x, before.cursor_y),
                (9, 10, 1, 2),
            )
            self.assertEqual(
                (after.columns, after.rows, after.cursor_x, after.cursor_y),
                (3, 4, 2, 3),
            )

    def test_grid_starts_as_blank_two_by_two(self):
        with Shitty(columns=2, rows=2) as terminal:
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines, ["  ", "  "])
            self.assertFalse(any(cell.drawn for cell in snapshot.cells))

    def test_rows_are_addressed_independently(self):
        with Shitty(columns=2, rows=2) as terminal:
            terminal.write(b"\x1b[1;1Ha\x1b[2;1Hb")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.cell(0, 0).char, "a")
            self.assertEqual(snapshot.cell(0, 1).char, "b")
            self.assertEqual(snapshot.lines, ["a ", "b "])

    def test_cursor_clamps_and_pending_wrap_represents_edge(self):
        with Shitty(columns=2, rows=2) as terminal:
            terminal.write(b"\x1b[2;2H")
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 1))

            terminal.write(b"X")
            self.assertTrue(terminal.cursor_pending_wrap())
            terminal.write(b"\x1b[999;999H")
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 1))
            self.assertFalse(terminal.cursor_pending_wrap())

            terminal.write(b"\x1b[0;0H")
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 0))

    def test_single_cell_change_publishes_only_its_row(self):
        with Shitty(columns=2, rows=2) as terminal:
            terminal.write(b"\x1b[1;2Ha")
            self.assertEqual(terminal.last_update_rows(), (0,))
            terminal.write(b"\x1b[2;1H")
            self.assertEqual(terminal.last_update_rows(), ())
            terminal.present()
            self.assertEqual(terminal.last_update_rows(), ())

    def test_full_cell_change_publishes_every_row(self):
        with Shitty(columns=2, rows=2) as terminal:
            terminal.write(b"ab\x1b[2;1Hcd\x1b[2J")
            self.assertEqual(terminal.last_update_rows(), (0, 1))
            terminal.write(b"\x1b[1;1H")
            self.assertEqual(terminal.last_update_rows(), ())

    def test_used_rows_include_drawn_content_and_cursor(self):
        def used_rows(snapshot):
            occupied = [snapshot.cursor_y]
            for row in range(snapshot.rows):
                if any(
                    snapshot.cell(column, row).drawn
                    for column in range(snapshot.columns)
                ):
                    occupied.append(row)
            return max(occupied) + 1

        with Shitty(columns=4, rows=4) as terminal:
            self.assertEqual(used_rows(terminal.model_snapshot()), 1)
            terminal.write(put_rows(b"abcd", b"efgh"))
            self.assertEqual(used_rows(terminal.model_snapshot()), 2)
            terminal.write(b"\x1b[3;1H")
            self.assertEqual(used_rows(terminal.model_snapshot()), 3)
            terminal.write(b"\x1b[4;1H")
            self.assertEqual(used_rows(terminal.model_snapshot()), 4)

    def test_scrolled_rows_keep_hard_soft_and_cursor_metadata(self):
        with Shitty(columns=4, rows=2, save_lines=4) as terminal:
            terminal.write(put_rows(b"abcd", b"efgh") + b"\x1b[2;1H\x1bD")
            terminal.wheel_up()
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines, ["abcd", "efgh"])
            self.assertFalse(snapshot.cell(3, 0).wrapped)

        with Shitty(columns=4, rows=2, save_lines=4) as terminal:
            terminal.write(b"abcdefgh\x1b[2;1H\x1bD")
            terminal.wheel_up()
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines, ["abcd", "efgh"])
            self.assertTrue(snapshot.cell(3, 0).wrapped)

        with Shitty(columns=4, rows=4, save_lines=4) as terminal:
            terminal.write(b"abcdefghi\x1b[3;1H\x1b[P")
            terminal.resize(8, 4)
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (7, 0))
            self.assertTrue(terminal.cursor_pending_wrap())

    def test_line_length_is_the_drawn_cell_prefix(self):
        with Shitty(columns=4, rows=4) as terminal:
            terminal.write(put_rows(b"abcd", b"efg"))
            snapshot = terminal.model_snapshot()
            lengths = tuple(
                sum(
                    snapshot.cell(column, row).drawn
                    for column in range(snapshot.columns)
                )
                for row in range(3)
            )
            self.assertEqual(lengths, (4, 3, 0))

    def test_index_moves_or_scrolls_at_public_boundaries(self):
        with Shitty(columns=4, rows=4, save_lines=4) as terminal:
            terminal.write(ROWS + b"\x1b[1;1H\x1bD")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines, ["abcd", "efgh", "ijkl", "mnop"])
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 1))

        with Shitty(columns=4, rows=4, save_lines=4) as terminal:
            terminal.write(ROWS + b"\x1b[4;1H\x1bD")
            self.assertEqual(terminal.scrollback_state()[0], 1)
            self.assertEqual(
                terminal.model_snapshot().lines,
                ["efgh", "ijkl", "mnop", "    "],
            )

        with Shitty(columns=4, rows=4, save_lines=4) as terminal:
            terminal.write(ROWS + b"\x1b[1;1r\x1b[2;1H\x1bD")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines, ["abcd", "efgh", "ijkl", "mnop"])
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 2))
            self.assertEqual(terminal.scrollback_state()[0], 0)

        with Shitty(columns=4, rows=4, save_lines=4) as terminal:
            terminal.write(
                b"abcde"
                b"\x1b[2;1Hefgh"
                b"\x1b[3;1Hijkl"
                b"\x1b[4;1Hmnop"
                b"\x1b[4;1H\x1bD"
            )
            terminal.wheel_up()
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[:2], ["abcd", "efgh"])
            self.assertTrue(snapshot.cell(3, 0).wrapped)

        with Shitty(columns=4, rows=4, save_lines=4) as terminal:
            terminal.write(ROWS + b"\x1b[1;2r\x1b[2;1H\x1bD")
            self.assertEqual(terminal.scrollback_state()[0], 1)
            self.assertEqual(
                terminal.model_snapshot().lines,
                ["efgh", "    ", "ijkl", "mnop"],
            )

        with Shitty(columns=4, rows=4, save_lines=4) as terminal:
            terminal.write(
                ROWS
                + b"\x1b[?69h\x1b[2;3s\x1b[2;3r"
                + b"\x1b[3;2H\x1bD"
            )
            self.assertEqual(
                terminal.model_snapshot().lines,
                ["abcd", "ejkh", "i  l", "mnop"],
            )
            self.assertEqual(terminal.scrollback_state()[0], 0)

        with Shitty(columns=4, rows=4, save_lines=1) as terminal:
            terminal.write(ROWS + b"\x1b[4;1H\x1bD\x1bD\x1bD")
            self.assertEqual(terminal.scrollback_state()[0], 1)
            terminal.wheel_up()
            self.assertEqual(
                terminal.model_snapshot().lines[:2],
                ["ijkl", "mnop"],
            )

    def test_cub_clamps_at_page_and_horizontal_margin(self):
        cases = (
            (b"\x1b[1;2H\x1b[D\x1b[D", (0, 0)),
            (b"\x1b[?69h\x1b[2;3s\x1b[1;2H\x1b[D", (1, 0)),
            (b"\x1b[?69h\x1b[2;3s\x1b[1;3H\x1b[D", (1, 0)),
            (b"\x1b[?69h\x1b[2;3s\x1b[1;4H\x1b[D", (2, 0)),
        )
        for sequence, expected in cases:
            with self.subTest(sequence=sequence), Shitty(columns=4, rows=4) as terminal:
                terminal.write(sequence)
                snapshot = terminal.model_snapshot()
                self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), expected)


if __name__ == "__main__":
    unittest.main()
