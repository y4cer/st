# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Public adaptations of iTerm2's legacy VT100ScreenTest methods."""

import unittest

from harness import Shitty


PORTED_CASES = (
    ("testInit", "test_legacy_init"),
    ("testDestructivelySetScreenWidthHeight", "test_destructive_geometry"),
    ("testSetSizeRespectsContinuations", "test_resize_preserves_wrapped_attributes"),
    ("testAppendingWithWraparoundOffSetsContinuation", "test_wraparound_off"),
    ("testSetSizeHeight", "test_resize_height_and_reflow"),
    ("testRunByTrimmingNullsFromRun", "test_public_rows_trim_terminal_nulls"),
    ("testTerminalResetPreservingPrompt", "test_ris_replaces_private_prompt_reset"),
    ("testAllCharacterSetPropertiesHaveDefaultValues", "test_charset_reset"),
    ("testClearBuffer", "test_public_clear_buffer_transaction"),
    ("testClearScrollbackBuffer", "test_erase_saved_lines"),
    ("testAppendStringAtCursorAscii", "test_ascii_attributes"),
    ("testAppendComposedCharactersPiecewise", "test_piecewise_graphemes"),
    ("testUnicode12Emoji", "test_unicode_emoji_zwj_sequence"),
    ("testAppendStringAtCursorNonAscii", "test_non_ascii_graphemes"),
    ("testLinefeed", "test_linefeed_regions_and_bounded_history"),
    ("testSetHistory", "test_stream_builds_equivalent_history"),
    ("testSetAltScreen", "test_stream_builds_equivalent_alt_page"),
    ("testSetTmuxState", "test_wire_state_equivalent_to_tmux_restore"),
    ("testSetFromFrame", "test_alt_page_resize_replaces_private_dvr_frame"),
    ("testNumberOfLines", "test_number_of_physical_rows_with_history"),
)


def write_lines(terminal, *lines):
    for line in lines:
        terminal.write(line.encode("utf-8") + b"\r\n")


def cell_codepoints(cell):
    if cell.grapheme:
        return cell.grapheme
    if cell.char not in ("\0", " "):
        return (ord(cell.char),)
    return ()


class ITerm2LegacyScreenTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_executable_cases(self):
        self.assertEqual(len(PORTED_CASES), 20)
        self.assertEqual(len({source for source, _ in PORTED_CASES}), 20)
        self.assertEqual(len({test for _, test in PORTED_CASES}), 20)
        for _, test in PORTED_CASES:
            self.assertTrue(callable(getattr(self, test)))

    def test_legacy_init(self):
        with Shitty(columns=17, rows=4, save_lines=8) as terminal:
            initial = terminal.model_snapshot()
            self.assertEqual((initial.columns, initial.rows), (17, 4))
            self.assertEqual((initial.cursor_x, initial.cursor_y), (0, 0))
            self.assertEqual(initial.lines, [" " * 17] * 4)
            self.assertTrue(terminal.tab_stop(8))
            self.assertTrue(terminal.tab_stop(16))
            terminal.write(b"\r\t")
            self.assertEqual(terminal.model_snapshot().cursor_x, 8)
            terminal.write(b"\r")

            write_lines(terminal, "Line 0", "Line 1", "Line 2", "Line 3")
            self.assertEqual(
                terminal.all_text(),
                ("Line 0", "Line 1", "Line 2", "Line 3", ""),
            )
            self.assertGreater(terminal.scrollback_state()[0], 0)

    def test_destructive_geometry(self):
        with Shitty(columns=6, rows=3) as terminal:
            terminal.write(b"\x1b#8")
            self.assertEqual(terminal.model_snapshot().lines, ["E" * 6] * 3)

            terminal.resize(7, 4)
            terminal.write(b"\x1bc")
            reset = terminal.model_snapshot()
            self.assertEqual((reset.columns, reset.rows), (7, 4))
            self.assertEqual(reset.lines, [" " * 7] * 4)
            self.assertEqual((reset.cursor_x, reset.cursor_y), (0, 0))

            terminal.write(b"1234561")
            self.assertEqual(terminal.model_snapshot().lines[0], "1234561")

    def test_resize_preserves_wrapped_attributes(self):
        with Shitty(columns=5, rows=4) as terminal:
            terminal.write(b"\x1b[44mABCDE\x1b[0mF")
            before = terminal.model_snapshot()
            blue = before.cell(0, 0).background
            default = before.cell(0, 1).background
            self.assertEqual(before.lines[:2], ["ABCDE", "F    "])

            terminal.resize(6, 4)
            after = terminal.model_snapshot()
            self.assertEqual(after.lines[0], "ABCDEF")
            self.assertEqual(
                [after.cell(column, 0).background for column in range(5)],
                [blue] * 5,
            )
            self.assertEqual(after.cell(5, 0).background, default)

    def test_wraparound_off(self):
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write(b"\x1b[?7l\x1b[45m0123456789Z")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines, ["0123Z", " " * 5, " " * 5])
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (4, 0))
            self.assertNotEqual(
                snapshot.cell(4, 0).background,
                snapshot.cell(0, 1).background,
            )
            terminal.write(b"\x1b[?7hX")
            self.assertEqual(terminal.model_snapshot().lines[0], "0123X")

    def test_resize_height_and_reflow(self):
        def make():
            terminal = Shitty(columns=5, rows=4, save_lines=20)
            terminal.write(b"abcdefgh\r\nijkl\r\n")
            return terminal

        terminal = make()
        try:
            before = terminal.model_digest()
            terminal.resize(5, 4)
            self.assertEqual(terminal.model_digest(), before)
            self.assertEqual(terminal.model_snapshot().lines, [
                "abcde", "fgh  ", "ijkl ", "     ",
            ])
        finally:
            terminal.close()

        terminal = make()
        try:
            terminal.resize(4, 4)
            self.assertEqual(terminal.model_snapshot().lines, [
                "abcd", "efgh", "ijkl", "    ",
            ])
        finally:
            terminal.close()

        terminal = make()
        try:
            terminal.resize(9, 4)
            self.assertEqual(terminal.model_snapshot().lines, [
                "abcdefgh ", "ijkl     ", " " * 9, " " * 9,
            ])
        finally:
            terminal.close()

        terminal = make()
        try:
            terminal.resize(5, 5)
            self.assertEqual(terminal.model_snapshot().lines, [
                "abcde", "fgh  ", "ijkl ", "     ", "     ",
            ])
        finally:
            terminal.close()

        terminal = make()
        try:
            terminal.resize(3, 3)
            self.assertEqual(terminal.model_snapshot().lines, ["ijk", "l  ", "   "])
            self.assertGreater(terminal.scrollback_state()[0], 0)
        finally:
            terminal.close()

    def test_public_rows_trim_terminal_nulls(self):
        with Shitty(columns=6, rows=3) as terminal:
            terminal.write(
                b"\x1b[1;3H1234"
                b"\x1b[2;1H56789a"
                b"\x1b[3;1Hbc"
            )
            self.assertEqual(terminal.all_text(), ("  1234", "56789a", "bc"))

        with Shitty(columns=6, rows=4) as terminal:
            terminal.write(b"\x1b[2;2H12345\x1b[3;1H67")
            self.assertEqual(terminal.all_text(), ("", " 12345", "67", ""))

        with Shitty(columns=4, rows=2) as terminal:
            self.assertEqual(terminal.all_text(), ("", ""))
            terminal.write(b"1234\x1b[2;1H5678")
            self.assertEqual(terminal.all_text(), ("1234", "5678"))

    def test_ris_replaces_private_prompt_reset(self):
        for marked_prompt in (False, True):
            with self.subTest(marked_prompt=marked_prompt):
                with Shitty(columns=5, rows=3, save_lines=1) as terminal:
                    default_charset = terminal.charset_state()
                    default_tabs = terminal.tab_stops()
                    if marked_prompt:
                        terminal.write(b"\x1b]133;A\x07")
                    terminal.write(b"abcdefgh\r\nijkl\r\n")
                    terminal.write(b"\x1b[2;3r\x1b[?69h\x1b[2;4s\x1b(0")
                    self.assertGreater(terminal.scrollback_state()[0], 0)

                    terminal.write(b"\x1bc")
                    reset = terminal.model_snapshot()
                    self.assertEqual(reset.lines, [" " * 5] * 3)
                    self.assertEqual((reset.cursor_x, reset.cursor_y), (0, 0))
                    self.assertEqual(terminal.scrollback_state()[0], 0)
                    self.assertEqual(terminal.charset_state(), default_charset)
                    self.assertEqual(terminal.tab_stops(), default_tabs)

    def test_charset_reset(self):
        with Shitty(columns=8, rows=2) as terminal:
            initial = terminal.charset_state()
            terminal.write(b"\x1b(0q\x0e\x1b)0q")
            changed = terminal.charset_state()
            self.assertNotEqual(changed, initial)
            before = terminal.model_snapshot().lines

            terminal.write(b"\x1b[!p")
            self.assertEqual(terminal.charset_state(), initial)
            self.assertEqual(terminal.model_snapshot().lines, before)

    def test_public_clear_buffer_transaction(self):
        with Shitty(columns=5, rows=4, save_lines=20) as terminal:
            write_lines(terminal, "abcdefgh", "ijkl", "mnopqrstuvwxyz")
            self.assertGreater(terminal.scrollback_state()[0], 0)
            terminal.write(b"\x1b[2J\x1b[3J\x1b[r\x1b[?69l\x1b[H")
            cleared = terminal.model_snapshot()
            self.assertEqual(cleared.lines, [" " * 5] * 4)
            self.assertEqual((cleared.cursor_x, cleared.cursor_y), (0, 0))
            self.assertEqual(terminal.scrollback_state()[0], 0)

    def test_erase_saved_lines(self):
        with Shitty(columns=5, rows=4, save_lines=20) as terminal:
            write_lines(terminal, "abcdefgh", "ijkl", "mnopqrstuvwxyz")
            before = terminal.model_snapshot().lines
            terminal.wheel_up(100)
            terminal.select_start(0, 0)
            terminal.select_update(3, 1)
            self.assertTrue(terminal.has_selection())

            terminal.write(b"\x1b[3J")
            self.assertEqual(terminal.scrollback_state()[0], 0)
            self.assertEqual(terminal.model_snapshot().lines, before)
            self.assertFalse(terminal.has_selection())
            self.assertEqual(terminal.last_update_rows(), tuple(range(4)))

    def test_ascii_attributes(self):
        with Shitty(columns=5, rows=4) as terminal:
            terminal.write(
                b"\x1b[38;5;5;48;5;6;1;3;4;5;9mHello world"
            )
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines, ["Hello", " worl", "d    ", "     "])
            cell = snapshot.cell(0, 0)
            self.assertEqual((cell.foreground_index, cell.background_index), (5, 6))
            self.assertTrue(cell.bold)
            self.assertTrue(cell.italic)
            self.assertTrue(cell.blink)
            self.assertTrue(cell.underline)
            self.assertTrue(cell.strike)

    def test_piecewise_graphemes(self):
        with self.subTest("ascii base plus combining mark"):
            with Shitty(columns=20, rows=2) as terminal:
                terminal.write_chunks(b"a", "\u0301".encode())
                cell = terminal.model_snapshot().cell(0, 0)
                self.assertEqual(cell_codepoints(cell), (0x61, 0x301))
                self.assertFalse(cell.double_width)

        with self.subTest("UTF-8 scalar split across writes"):
            with Shitty(columns=20, rows=2) as terminal:
                encoded = "\U00010150".encode()
                terminal.write_chunks(encoded[:2], encoded[2:])
                self.assertEqual(
                    cell_codepoints(terminal.model_snapshot().cell(0, 0)),
                    (0x10150,),
                )

        with self.subTest("wide base plus combining mark"):
            with Shitty(columns=20, rows=2) as terminal:
                terminal.write_chunks("Ｅ".encode(), "\u0301".encode())
                snapshot = terminal.model_snapshot()
                self.assertEqual(
                    cell_codepoints(snapshot.cell(0, 0)),
                    (0xFF25, 0x301),
                )
                self.assertTrue(snapshot.cell(0, 0).double_width)
                self.assertTrue(snapshot.cell(1, 0).double_width_continuation)

        with self.subTest("default-ignorable before standalone modifier"):
            with Shitty(columns=20, rows=2) as terminal:
                terminal.write_chunks("\ufeff".encode(), "\U0001f3fe".encode())
                snapshot = terminal.model_snapshot()
                self.assertEqual(cell_codepoints(snapshot.cell(0, 0)), (0x1F3FE,))
                self.assertTrue(snapshot.cell(0, 0).double_width)
                self.assertTrue(snapshot.cell(1, 0).double_width_continuation)

    def test_unicode_emoji_zwj_sequence(self):
        sequence = "👨🏿‍🤝‍👨🏻"
        with Shitty(columns=20, rows=2) as terminal:
            chunks = [character.encode("utf-8") for character in sequence]
            terminal.write_chunks(*chunks)
            snapshot = terminal.model_snapshot()
            self.assertEqual(
                snapshot.cell(0, 0).grapheme,
                tuple(ord(character) for character in sequence),
            )
            self.assertTrue(snapshot.cell(0, 0).double_width)
            self.assertTrue(snapshot.cell(1, 0).double_width_continuation)

    def test_non_ascii_graphemes(self):
        text = "\u0301a\u0301a\u0301\u0327\U00010150Ｅ\u0301\ufeff\u200b\u200c\u200dgł🖕🏾g🏾"
        with Shitty(columns=20, rows=2) as terminal:
            terminal.write(b"\x1b[38;5;5;48;5;6;1;3;4;5;9m")
            terminal.write(text.encode("utf-8"))
            snapshot = terminal.model_snapshot()
            cell = next(
                snapshot.cell(column, 0)
                for column in range(snapshot.columns)
                if cell_codepoints(snapshot.cell(column, 0))
            )
            self.assertEqual((cell.foreground_index, cell.background_index), (5, 6))
            self.assertTrue(cell.bold)
            self.assertTrue(cell.italic)
            self.assertTrue(cell.blink)
            self.assertTrue(cell.underline)
            self.assertTrue(cell.strike)

    def test_linefeed_regions_and_bounded_history(self):
        with Shitty(columns=5, rows=5, save_lines=20) as terminal:
            write_lines(terminal, "abcdefgh", "ijkl", "mnop")
            terminal.write(b"\x1b[2;4r\x1b[?69h\x1b[2;4s\x1b[4;4H\n")
            self.assertEqual(terminal.model_snapshot().lines, [
                "abcde", "fjkl ", "inop ", "m    ", "     ",
            ])
            self.assertEqual(terminal.model_snapshot().cursor_x, 3)

        with Shitty(columns=5, rows=5, save_lines=1) as terminal:
            write_lines(terminal, "abcdefgh", "ijkl", "mnop")
            terminal.write(b"\x1b[5;4H\n\n")
            self.assertEqual(terminal.model_snapshot().lines, [
                "ijkl ", "mnop ", "     ", "     ", "     ",
            ])
            self.assertEqual(terminal.scrollback_state()[0], 1)
            self.assertEqual(terminal.model_snapshot().cursor_x, 3)

    def test_stream_builds_equivalent_history(self):
        lines = (
            "abcdefghijkl", "mnop", "qrstuvwxyz", "0123456  ",
            "ABC   ", "DEFGHIJKL   ", "MNOP  ",
        )
        with Shitty(columns=6, rows=4, save_lines=32) as terminal:
            for index, line in enumerate(lines):
                terminal.write(line.encode())
                if index + 1 != len(lines):
                    terminal.write(b"\r\n")
            self.assertEqual(terminal.all_text(), (
                "abcdef", "ghijkl", "mnop", "qrstuv", "wxyz", "012345",
                "6  ", "ABC   ", "DEFGHI", "JKL   ", "MNOP  ",
            ))

    def test_stream_builds_equivalent_alt_page(self):
        with Shitty(columns=6, rows=4, save_lines=20) as terminal:
            terminal.write(b"primary\x1b[?1049h\x1b[Habcdefghijkl\r\nmnop\r\nqrstuv")
            self.assertEqual(terminal.model_snapshot().lines, [
                "abcdef", "ghijkl", "mnop  ", "qrstuv",
            ])
            self.assertEqual(terminal.scrollback_state()[0], 0)
            terminal.write(b"\x1b[?1049l")
            self.assertTrue(terminal.model_snapshot().lines[0].startswith("primar"))

    def test_wire_state_equivalent_to_tmux_restore(self):
        with Shitty(columns=10, rows=10) as terminal:
            terminal.write(
                b"\x1b[?25l"
                b"\x1b[7;8r"
                b"\x1b[3g"
                b"\x1b[1;5H\x1bH"
                b"\x1b[1;9H\x1bH"
                b"\x1b[6;5H"
            )
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (4, 5))
            self.assertEqual(snapshot.cursor_style, 0)
            self.assertEqual(
                tuple(i for i, stop in enumerate(terminal.tab_stops()) if stop),
                (4, 8),
            )
            terminal.write(b"\r\t\t")
            self.assertEqual(terminal.model_snapshot().cursor_x, 8)

    def test_alt_page_resize_replaces_private_dvr_frame(self):
        with Shitty(columns=5, rows=4, save_lines=0) as terminal:
            terminal.write(b"\x1b[?1049habcdefgh\r\nijkl")
            source = terminal.model_snapshot()
            self.assertEqual(source.lines, ["abcde", "fgh  ", "ijkl ", "     "])
            terminal.resize(2, 2)
            resized = terminal.model_snapshot()
            self.assertEqual((resized.columns, resized.rows), (2, 2))
            self.assertEqual(resized.lines, ["fg", "ij"])
            self.assertEqual((resized.cursor_x, resized.cursor_y), (1, 1))

    def test_number_of_physical_rows_with_history(self):
        with Shitty(columns=5, rows=2, save_lines=20) as terminal:
            self.assertEqual(len(terminal.all_text()), 2)
            write_lines(terminal, "abcdefgh", "ijkl", "mnopqrstuvwxyz", "012")
            self.assertEqual(terminal.all_text(), (
                "abcde", "fgh", "ijkl", "mnopq", "rstuv", "wxyz", "012", "",
            ))


if __name__ == "__main__":
    unittest.main()
