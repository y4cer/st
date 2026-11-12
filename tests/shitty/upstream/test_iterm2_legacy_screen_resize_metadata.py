# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Fourth public batch from iTerm2's legacy VT100ScreenTest."""

import unittest

from harness import Shitty, put_rows


PORTED_CASES = (
    ("testEraseCharactersAfterCursor", "test_ech_counts_wrap_and_wide_boundaries"),
    ("testSetTitle", "test_window_and_icon_titles_survive_scrollback"),
    ("testInsertEmptyCharsAtCursor", "test_ich_counts_margins_and_wide_boundaries"),
    ("testInsertBlankLinesAfterCursor", "test_il_counts_regions_and_soft_wrap"),
    ("testDeleteLinesAtCursor", "test_dl_counts_regions_and_soft_wrap"),
    ("testTerminalSetPixelSize", "test_pixel_resize_omitted_zero_and_fixed_dimensions"),
    ("testScrollUp", "test_su_counts_history_and_rectangular_region"),
    ("testPasting", "test_application_clipboard_write_reaches_host"),
    ("testCursorReporting", "test_dsr_reports_cursor_position"),
    ("testReportWindowSize", "test_xtwinops_reports_character_size"),
    ("testResizeNotes", "test_primary_range_metadata_reflows_while_alt_is_active"),
    ("testRestoreWithNoteOnEmptyLineAtTop", "test_empty_cell_annotation_can_be_attached"),
    ("testResizeWithSelectionOfJustNullsInAltScreen", "test_alt_blank_selection_is_cleared_on_width_change"),
    ("testResizeWithSelectionOfJustNullsInMainScreen", "test_main_blank_selection_is_cleared_on_width_change"),
    ("testResizeNoteInPrimaryWhileInAltAndSomeHistory", "test_primary_history_range_metadata_reflows_while_inactive"),
    ("testResizeNoteInPrimaryWhileInAltAndPushingSomePrimaryIncludingWholeNoteIntoHistory", "test_whole_metadata_range_can_move_through_history"),
    ("testResizeNoteInPrimaryWhileInAltAndPushingSomePrimaryIncludingPartOfNoteIntoHistory", "test_partial_metadata_range_can_move_through_history"),
    ("testNoteTruncatedOnSwitchingToAlt", "test_buffer_round_trip_preserves_supported_range_metadata"),
    ("testResizeNoteInAlternateThatGetsTruncatedByShrinkage", "test_alt_resize_keeps_metadata_on_surviving_cells"),
    ("testResizeWithNoteFirstLine", "test_annotation_state_round_trip_preserves_range"),
)

URI = b"https://example.test/iterm2-note"


def osc8(uri=URI):
    return b"\x1b]8;;" + uri + b"\x1b\\"


def close_osc8():
    return osc8(b"")


def wrapped_fixture(columns=10, rows=3):
    terminal = Shitty(columns=columns, rows=rows, save_lines=20)
    terminal.write(b"abcdefghijklm")
    return terminal


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


def five_by_four(link=b""):
    """The public form of fiveByFourScreenWithThreeLinesOneWrapped."""
    terminal = Shitty(columns=5, rows=4, save_lines=20)
    if link == b"fg":
        terminal.write(b"abcde" + osc8() + b"fg" + close_osc8() + b"h\r\nijkl\r\n")
    elif link == b"ij":
        terminal.write(b"abcdefgh\r\n" + osc8() + b"ij" + close_osc8() + b"kl\r\n")
    else:
        terminal.write(b"abcdefgh\r\nijkl\r\n")
    return terminal


def history_fixture(link_from=b"", link_to=b""):
    """Build abcdefgh, ijkl, hello world with one linked content range."""
    terminal = Shitty(columns=5, rows=4, save_lines=20)
    parts = (
        (b"abcde", b"abcde"),
        (b"fgh", b"fgh"),
        (b"\r\n", b""),
        (b"ijkl", b"ijkl"),
        (b"\r\n", b""),
        (b"hello", b"hello"),
        (b" world", b" world"),
    )
    active = False
    for payload, name in parts:
        if name == link_from:
            terminal.write(osc8())
            active = True
        terminal.write(payload)
        if name == link_to:
            terminal.write(close_osc8())
            active = False
    if active:
        terminal.write(close_osc8())
    return terminal


class ITerm2LegacyScreenResizeMetadataTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_executable_cases(self):
        self.assertEqual(len(PORTED_CASES), 20)
        self.assertEqual(len({source for source, _ in PORTED_CASES}), 20)
        self.assertEqual(len({test for _, test in PORTED_CASES}), 20)
        for _, test in PORTED_CASES:
            self.assertTrue(callable(getattr(self, test)))

    def test_ech_counts_wrap_and_wide_boundaries(self):
        # ECMA-48 makes an omitted or zero count one, unlike the private
        # zero-distance method called by the old iTerm2 test.
        for parameter in (b"", b"0"):
            with self.subTest(parameter=parameter):
                terminal = wrapped_fixture()
                try:
                    terminal.write(b"\x1b[1;5H\x1b[" + parameter + b"X")
                    self.assertEqual(terminal.snapshot().lines[0], "abcd fghij")
                finally:
                    terminal.close()

        for count, expected in ((2, "abcd  ghij"), (6, "abcd      "), (100, "abcd      ")):
            with self.subTest(count=count):
                terminal = wrapped_fixture()
                try:
                    terminal.write(f"\x1b[1;5H\x1b[{count}X".encode())
                    self.assertEqual(terminal.snapshot().lines[0], expected)
                finally:
                    terminal.close()

        wide_cases = (
            (b"abc" + "界".encode() + b"fghij", b"\x1b[1;5H\x1b[2X", "abc   ghij"),
            (b"abcde" + "界".encode() + b"hij", b"\x1b[1;5H\x1b[2X", "abcd   hij"),
        )
        for content, command, expected in wide_cases:
            with self.subTest(expected=expected), Shitty(columns=10, rows=2) as terminal:
                terminal.write(content + command)
                snapshot = terminal.snapshot()
                self.assertEqual(snapshot.lines[0], expected)
                assert_complete_wide(self, snapshot)

        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(b"abcdefghi" + "界".encode() + b"klm")
            before = terminal.snapshot()
            self.assertTrue(before.cell(0, 1).double_width)
            terminal.write(b"\x1b[1;5H\x1b[6X")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0], "abcd      ")
            self.assertEqual(snapshot.cell(0, 1).char, "界")
            assert_complete_wide(self, snapshot)

    def test_window_and_icon_titles_survive_scrollback(self):
        with Shitty(
            columns=10,
            rows=4,
            save_lines=20,
            extra_arguments=("-allowWindowOps", "true"),
        ) as terminal:
            terminal.write(b"\x1b]2;test\x1b\\")
            self.assertEqual(terminal.window_title(), "test")
            terminal.write(b"\x1b]2;test2\x1b\\")
            self.assertEqual(terminal.window_title(), "test2")

            terminal.write((b"line\r\n" * 30) + b"\x1b]2;test\x1b\\")
            self.assertEqual(terminal.window_title(), "test")
            self.assertEqual(terminal.scrollback_state()[0], 20)

            terminal.write(b"\x1b]1;test3\x1b\\\x1b[20t\x1b[21t")
            self.assertEqual(
                terminal.read_input(),
                b"\x1b]Ltest3\x1b\\\x1b]ltest\x1b\\",
            )
            terminal.write(b"\x1b]1;test4\x1b\\\x1b[20t")
            self.assertEqual(terminal.read_input(), b"\x1b]Ltest4\x1b\\")

    def test_ich_counts_margins_and_wide_boundaries(self):
        for parameter, expected in (
            (b"", "abcd efghi"),
            (b"0", "abcd efghi"),
            (b"2", "abcd  efgh"),
            (b"6", "abcd      "),
            (b"100", "abcd      "),
        ):
            with self.subTest(parameter=parameter):
                terminal = wrapped_fixture()
                try:
                    terminal.write(b"\x1b[1;5H\x1b[" + parameter + b"@")
                    self.assertEqual(terminal.snapshot().lines[0], expected)
                finally:
                    terminal.close()

        wide_cases = (
            (b"abcd" + "界".encode() + b"fghi", b"\x1b[1;6H\x1b[@", "abcd   fgh"),
            (b"abc" + "界".encode() + b"efghi", b"\x1b[1;5H\x1b[@", "abc   efgh"),
            (b"abcdefgh" + "界".encode(), b"\x1b[1;5H\x1b[@", "abcd efgh "),
        )
        for content, command, expected in wide_cases:
            with self.subTest(expected=expected), Shitty(columns=10, rows=2) as terminal:
                terminal.write(content + command)
                snapshot = terminal.snapshot()
                self.assertEqual(snapshot.lines[0], expected)
                assert_complete_wide(self, snapshot)

        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(b"abcdefghijklm\x1b[?69h\x1b[3;9s\x1b[1;5H\x1b[@")
            self.assertEqual(terminal.snapshot().lines[0], "abcd efghj")

    def test_il_counts_regions_and_soft_wrap(self):
        page = b"abcdefg\r\nhij"
        for parameter in (b"", b"0"):
            with self.subTest(parameter=parameter), Shitty(columns=4, rows=4) as terminal:
                terminal.write(page + b"\x1b[2;4H\x1b[" + parameter + b"L")
                self.assertEqual(terminal.snapshot().lines, ["abcd", "    ", "efg ", "hij "])

        with Shitty(columns=4, rows=4) as terminal:
            terminal.write(page + b"\x1b[2;4H\x1b[2L")
            self.assertEqual(terminal.snapshot().lines, ["abcd", "    ", "    ", "efg "])

        for setup in (
            b"\x1b[2;3r\x1b[1;1H",
            b"\x1b[?69h\x1b[2;3s\x1b[1;1H",
        ):
            with self.subTest(setup=setup), Shitty(columns=4, rows=4) as terminal:
                terminal.write(page + setup)
                before = terminal.model_digest()
                terminal.write(b"\x1b[L")
                self.assertEqual(terminal.model_digest(), before)

    def test_dl_counts_regions_and_soft_wrap(self):
        page = b"abcdefg\r\nhij"
        for parameter in (b"", b"0"):
            with self.subTest(parameter=parameter), Shitty(columns=4, rows=4) as terminal:
                terminal.write(page + b"\x1b[2;4H\x1b[" + parameter + b"M")
                self.assertEqual(terminal.snapshot().lines, ["abcd", "hij ", "    ", "    "])

        for setup in (
            b"\x1b[2;3r\x1b[1;1H",
            b"\x1b[?69h\x1b[2;3s\x1b[1;1H",
        ):
            with self.subTest(setup=setup), Shitty(columns=4, rows=4) as terminal:
                terminal.write(page + setup)
                before = terminal.model_digest()
                terminal.write(b"\x1b[M")
                self.assertEqual(terminal.model_digest(), before)

        with Shitty(columns=4, rows=5) as terminal:
            terminal.write(b"abcdefg\r\nhij\r\nklm")
            terminal.write(b"\x1b[2;3r\x1b[2;2H\x1b[M")
            self.assertEqual(
                terminal.snapshot().lines,
                ["abcd", "hij ", "    ", "klm ", "    "],
            )

    def test_pixel_resize_omitted_zero_and_fixed_dimensions(self):
        with Shitty(
            columns=10,
            rows=4,
            glyph_px=2,
            glyph_py=4,
            extra_arguments=("-allowWindowOps", "true"),
        ) as terminal:
            terminal.window_info(screen_width=30, screen_height=20)
            terminal.write(b"\x1b[4;;t")
            self.assertEqual(terminal.winsize_full(), (10, 4, 20, 16))
            self.assertEqual(terminal.read_actions(), ["WINDOW 4 20 24"])

            terminal.write(b"\x1b[4;0;0t")
            self.assertEqual(terminal.winsize_full(), (13, 4, 26, 16))
            self.assertEqual(terminal.read_actions(), ["WINDOW 4 20 30"])

            terminal.write(b"\x1b[4;60;50t")
            self.assertEqual(terminal.winsize_full(), (23, 14, 46, 56))
            self.assertEqual(terminal.read_actions(), ["WINDOW 4 60 50"])

    def test_su_counts_history_and_rectangular_region(self):
        for parameter in (b"", b"0"):
            with self.subTest(parameter=parameter), Shitty(
                columns=4, rows=4, save_lines=10
            ) as terminal:
                terminal.write(put_rows(b"abcd", b"efg", b"hij"))
                terminal.write(b"\x1b[" + parameter + b"S")
                self.assertEqual(terminal.all_text(), ("abcd", "efg", "hij", "", ""))

        with Shitty(columns=4, rows=4, save_lines=10) as terminal:
            terminal.write(put_rows(b"abcd", b"efg", b"hij") + b"\x1b[2S")
            self.assertEqual(
                terminal.all_text(),
                ("abcd", "efg", "hij", "", "", ""),
            )

        with Shitty(columns=4, rows=4) as terminal:
            terminal.write(
                put_rows(b"abcd", b"efg", b"hij")
                + b"\x1b[?69h\x1b[2;3s\x1b[2;3r\x1b[S"
            )
            self.assertEqual(terminal.snapshot().lines, ["abcd", "eij ", "h   ", "    "])

    def test_application_clipboard_write_reaches_host(self):
        # iTerm2's old OSC 50 CopyToClipboard framing is represented by the
        # interoperable OSC 52 operation implemented by the supporting vote.
        with Shitty() as terminal:
            terminal.set_system_clipboard(b"old")
            terminal.write(b"\x1b]52;c;SGVsbG8gd29ybGQ=\x1b\\")
            self.assertEqual(terminal.get_selection(primary=False), b"Hello world")

    def test_dsr_reports_cursor_position(self):
        with Shitty(columns=20, rows=20) as terminal:
            terminal.write(b"\x1b[3;2H\x1b[6n")
            self.assertEqual(terminal.read_input(), b"\x1b[3;2R")

    def test_xtwinops_reports_character_size(self):
        with Shitty(
            columns=30,
            rows=20,
            extra_arguments=("-allowWindowOps", "true"),
        ) as terminal:
            terminal.write(b"\x1b[18t")
            self.assertEqual(terminal.read_input(), b"\x1b[8;20;30t")

    def test_primary_range_metadata_reflows_while_alt_is_active(self):
        terminal = five_by_four(b"fg")
        try:
            terminal.write(b"\x1b[?1049h")
            terminal.resize(4, 4)
            terminal.write(b"\x1b[?1049l")
            self.assertEqual(terminal.snapshot().lines, ["abcd", "efgh", "ijkl", "    "])
            self.assertEqual(terminal.hyperlink(1, 1), URI.decode())
            self.assertEqual(terminal.hyperlink(2, 1), URI.decode())
            self.assertEqual(terminal.hyperlink(0, 1), "")
            self.assertEqual(terminal.hyperlink(3, 1), "")
        finally:
            terminal.close()

    @unittest.expectedFailure
    def test_empty_cell_annotation_can_be_attached(self):
        with Shitty(columns=5, rows=4) as terminal:
            operation = getattr(terminal, "attach_annotation", None)
            if operation is None:
                raise AssertionError(
                    "iTerm2 can anchor a note to untouched empty cells; no "
                    "other oracle or Shitty exposes that host operation"
                )
            annotation = operation((0, 3), (2, 3), "note")
            terminal.write(b"\x1b[?1049h\x1b[?1049l")
            self.assertEqual(annotation.range(), ((0, 3), (2, 3)))

    @unittest.expectedFailure
    def test_alt_blank_selection_is_cleared_on_width_change(self):
        with Shitty(columns=5, rows=4) as terminal:
            terminal.write(b"\x1b[?1049h")
            terminal.select_start(1, 1)
            terminal.select_extend(2, 2)
            self.assertTrue(terminal.has_selection())
            terminal.resize(4, 4)
            self.assertFalse(terminal.has_selection())

    @unittest.expectedFailure
    def test_main_blank_selection_is_cleared_on_width_change(self):
        with Shitty(columns=5, rows=4) as terminal:
            terminal.select_start(1, 1)
            terminal.select_extend(2, 2)
            self.assertTrue(terminal.has_selection())
            terminal.resize(4, 4)
            self.assertFalse(terminal.has_selection())

    def test_primary_history_range_metadata_reflows_while_inactive(self):
        terminal = five_by_four(b"ij")
        try:
            terminal.write(b"hello world")
            self.assertEqual(terminal.all_text(), ("abcde", "fgh", "ijkl", "hello", " worl", "d"))
            terminal.write(b"\x1b[?1049h")
            terminal.resize(4, 4)
            terminal.write(b"\x1b[?1049l")
            self.assertEqual(terminal.snapshot().lines, ["ijkl", "hell", "o wo", "rld "])
            self.assertEqual(terminal.hyperlink(0, 0), URI.decode())
            self.assertEqual(terminal.hyperlink(1, 0), URI.decode())
            self.assertEqual(terminal.hyperlink(2, 0), "")
        finally:
            terminal.close()

    def test_whole_metadata_range_can_move_through_history(self):
        terminal = five_by_four(b"ij")
        try:
            terminal.write(b"hello world")
            terminal.write(b"\x1b[?1049h")
            terminal.resize(3, 4)
            terminal.write(b"\x1b[?1049l")
            terminal.resize(3, 9)
            self.assertEqual(terminal.hyperlink(0, 3), URI.decode())
            self.assertEqual(terminal.hyperlink(1, 3), URI.decode())
            self.assertEqual(terminal.hyperlink(2, 3), "")
            self.assertEqual(terminal.hyperlink(0, 4), "")
        finally:
            terminal.close()

    def test_partial_metadata_range_can_move_through_history(self):
        terminal = history_fixture(b"ijkl", b"hello")
        try:
            terminal.write(b"\x1b[?1049h")
            terminal.resize(3, 4)
            terminal.write(b"\x1b[?1049l")
            terminal.resize(3, 9)
            for column, row in ((0, 3), (1, 3), (2, 3), (0, 4), (0, 5), (1, 5), (2, 5), (0, 6), (1, 6)):
                self.assertEqual(terminal.hyperlink(column, row), URI.decode())
            self.assertEqual(terminal.hyperlink(2, 6), "")
            self.assertEqual(terminal.hyperlink(0, 7), "")
        finally:
            terminal.close()

    def test_buffer_round_trip_preserves_supported_range_metadata(self):
        terminal = history_fixture(b"fgh", b"hello")
        try:
            terminal.write(b"\x1b[?1049h\x1b[?1049l")
            terminal.resize(5, 6)
            self.assertEqual(terminal.snapshot().lines[:6], ["abcde", "fgh  ", "ijkl ", "hello", " worl", "d    "])
            for column, row in ((0, 1), (1, 1), (2, 1), (0, 2), (3, 2), (0, 3), (4, 3)):
                self.assertEqual(terminal.hyperlink(column, row), URI.decode())
            self.assertEqual(terminal.hyperlink(0, 0), "")
            self.assertEqual(terminal.hyperlink(0, 4), "")
        finally:
            terminal.close()

    def test_alt_resize_keeps_metadata_on_surviving_cells(self):
        with Shitty(columns=5, rows=4) as terminal:
            terminal.write(
                b"\x1b[?1049h\x1b[1;1H"
                + osc8()
                + b"FGH\x1b[2;1HIJKL\x1b[3;1HHELLO"
                + close_osc8()
                + b"\x1b[4;1HWORLD"
            )
            terminal.resize(3, 4)
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["FGH", "IJK", "HEL", "WOR"])
            for row in range(3):
                for column in range(3):
                    self.assertEqual(terminal.hyperlink(column, row), URI.decode())
            for column in range(3):
                self.assertEqual(terminal.hyperlink(column, 3), "")

    @unittest.expectedFailure
    def test_annotation_state_round_trip_preserves_range(self):
        with Shitty(columns=5, rows=9) as terminal:
            terminal.write(b"abcde\r\nfgh\r\nijkl")
            save = getattr(terminal, "save_annotation_state", None)
            restore = getattr(terminal, "restore_annotation_state", None)
            if save is None or restore is None:
                raise AssertionError(
                    "iTerm2 serializes host note objects and restores their "
                    "ranges; the other oracles and Shitty expose no such state"
                )
            state = save(((0, 0), (5, 0)), "note")
            terminal.resize(3, 4)
            annotation = restore(state)
            self.assertEqual(annotation.range(), ((0, 0), (5, 0)))


if __name__ == "__main__":
    unittest.main()
