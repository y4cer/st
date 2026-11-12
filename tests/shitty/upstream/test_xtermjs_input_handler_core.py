# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Public adaptations of the first 20 xterm.js InputHandler tests."""

import unittest

from harness import Shitty


UPSTREAM_CASES = (
    "SL (scrollLeft)",
    "SR (scrollRight)",
    "insertColumns (DECIC)",
    "deleteColumns (DECDC)",
    "BS reverseWraparound: should not reverse outside of scroll margins",
    "save and restore cursor",
    "DECSC/DECRC: should save and restore origin mode",
    "DECSC/DECRC: should save and restore wraparound mode",
    "setCursorStyle: should call Terminal.setOption with correct params",
    "setMode: should toggle bracketedPasteMode",
    "setMode: should toggle colorSchemeUpdates (DECSET 2031)",
    "setMode: should not toggle colorSchemeUpdates when colorSchemeQuery is disabled",
    "regression tests: insertChars",
    "regression tests: deleteChars",
    "regression tests: eraseInLine",
    "regression tests: eraseInLine reflow",
    "regression tests: ED2 with scrollOnEraseInDisplay turned on",
    "regression tests: eraseInDisplay",
    "print: should not cause an infinite loop (regression test)",
    "print: should join combining characters in a single print",
)


def mode_query(terminal, mode):
    terminal.write(f"\x1b[?{mode}$p".encode())
    return terminal.read_input()


def has_soft_wrap(snapshot, row):
    return any(snapshot.cell(column, row).wrapped for column in range(snapshot.columns))


class XtermJsInputHandlerCoreTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 20)
        self.assertEqual(len(set(UPSTREAM_CASES)), 20)

    def test_scroll_left_defaults_zero_and_explicit_counts(self):
        with Shitty(columns=5, rows=5, save_lines=1) as terminal:
            terminal.write(b"12345" * 6)
            self.assertEqual(terminal.scrollback_state()[0], 1)

            terminal.write(b"\x1b[ @")
            self.assertEqual(terminal.snapshot().lines, ["2345 "] * 5)
            terminal.write(b"\x1b[0 @")
            self.assertEqual(terminal.snapshot().lines, ["345  "] * 5)
            terminal.write(b"\x1b[2 @")
            self.assertEqual(terminal.snapshot().lines, ["5    "] * 5)

    def test_scroll_right_defaults_zero_and_explicit_counts(self):
        with Shitty(columns=5, rows=5, save_lines=1) as terminal:
            terminal.write(b"12345" * 6)
            self.assertEqual(terminal.scrollback_state()[0], 1)

            terminal.write(b"\x1b[ A")
            self.assertEqual(terminal.snapshot().lines, [" 1234"] * 5)
            terminal.write(b"\x1b[0 A")
            self.assertEqual(terminal.snapshot().lines, ["  123"] * 5)
            terminal.write(b"\x1b[2 A")
            self.assertEqual(terminal.snapshot().lines, ["    1"] * 5)

    def test_decic_defaults_zero_and_explicit_counts(self):
        expected = ((b"\x1b['}", "12 34"), (b"\x1b[1'}", "12 34"), (b"\x1b[2'}", "12  3"))
        for operation, line in expected:
            with self.subTest(operation=operation):
                with Shitty(columns=5, rows=5, save_lines=1) as terminal:
                    terminal.write(b"12345" * 6 + b"\x1b[3;3H" + operation)
                    self.assertEqual(terminal.snapshot().lines, [line] * 5)

    def test_decdc_defaults_zero_and_explicit_counts(self):
        expected = ((b"\x1b['~", "1245 "), (b"\x1b[1'~", "1245 "), (b"\x1b[2'~", "125  "))
        for operation, line in expected:
            with self.subTest(operation=operation):
                with Shitty(columns=5, rows=5, save_lines=1) as terminal:
                    terminal.write(b"12345" * 6 + b"\x1b[3;3H" + operation)
                    self.assertEqual(terminal.snapshot().lines, [line] * 5)

    @unittest.expectedFailure
    def test_reverse_wrap_stops_at_each_vertical_margin_boundary(self):
        tty_backspace = b"\x08 \x08"
        with Shitty(columns=5, rows=5, save_lines=1) as terminal:
            terminal.write(b"#####abcdefghijklmnopqrstuvwxy")
            terminal.write(tty_backspace * 100)
            self.assertEqual(
                terminal.snapshot().lines,
                ["abcde", "fghij", "klmno", "pqrst", "    y"],
            )

            terminal.write(b"\x1b[?45huvwxy\x1b[2;4r")
            terminal.write(b"\x1b[5;1Huvwxy" + tty_backspace * 100)
            self.assertEqual(terminal.snapshot().lines[-1], "     ")

            terminal.write(b"uvwxy\x1b[4;5Ht" + tty_backspace * 100)
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 1))
            self.assertEqual(snapshot.lines[4], "uvwxy")

            terminal.write(b"\x1b[3;1Hfghijklmnopqrst")
            terminal.write(b"\x1b[1;1H#####" + tty_backspace * 100)
            self.assertEqual(terminal.snapshot().lines[0], "#####")

    def test_save_and_restore_cursor_position_and_rendition(self):
        with Shitty(columns=20, rows=24) as terminal:
            terminal.write(
                b"\x1b[3;2H\x1b[31m\x1b7"
                b"\x1b[21;11H\x1b[30m\x1b8X"
            )
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (2, 2))
            self.assertEqual(snapshot.cell(1, 2).foreground_index, 1)

    def test_decsc_decrc_save_and_restore_origin_mode(self):
        with Shitty(columns=8, rows=4) as terminal:
            terminal.write(b"\x1b[?6h\x1b7\x1b[?6l\x1b8")
            self.assertEqual(mode_query(terminal, 6), b"\x1b[?6;1$y")

    @unittest.expectedFailure
    def test_decsc_decrc_save_and_restore_wraparound_mode(self):
        with Shitty(columns=8, rows=4) as terminal:
            terminal.write(b"\x1b[?7l\x1b7\x1b[?7h\x1b8")
            self.assertEqual(mode_query(terminal, 7), b"\x1b[?7;2$y")

    def test_decscusr_accepts_every_xtermjs_cursor_style_parameter(self):
        for style in range(7):
            with self.subTest(style=style):
                with Shitty(columns=8, rows=2) as terminal:
                    terminal.write(f"\x1b[{style} q\x1bP$q q\x1b\\".encode())
                    expected = style or 1
                    self.assertEqual(
                        terminal.read_input(),
                        f"\x1bP1$r{expected} q\x1b\\".encode(),
                    )

    def test_decset_toggles_bracketed_paste_mode(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[?2004h")
            self.assertEqual(mode_query(terminal, 2004), b"\x1b[?2004;1$y")
            terminal.write(b"\x1b[?2004l")
            self.assertEqual(mode_query(terminal, 2004), b"\x1b[?2004;2$y")

    def test_decset_toggles_color_scheme_update_mode(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[?2031h")
            self.assertEqual(mode_query(terminal, 2031), b"\x1b[?2031;1$y")
            terminal.write(b"\x1b[?2031l")
            self.assertEqual(mode_query(terminal, 2031), b"\x1b[?2031;2$y")

    @unittest.expectedFailure
    def test_disabled_color_scheme_query_extension_rejects_decset_2031(self):
        # xterm.js has a vtExtensions.colorSchemeQuery gate. Shitty currently
        # exposes no equivalent option, so the public DECSET remains active.
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[?2031h")
            self.assertEqual(mode_query(terminal, 2031), b"\x1b[?2031;2$y")

    def test_ich_zero_one_two_and_ten_are_clipped_at_the_right_edge(self):
        with Shitty(columns=80, rows=30) as terminal:
            terminal.write(b"a" * 70 + b"1234567890" + b"a" * 70 + b"1234567890")
            expected = (
                (b"\x1b[@", " " + "123456789"),
                (b"\x1b[1@", "  " + "12345678"),
                (b"\x1b[2@", "    " + "123456"),
                (b"\x1b[10@", " " * 10),
            )
            for operation, suffix in expected:
                terminal.write(b"\x1b[1;71H" + operation)
                self.assertEqual(terminal.snapshot().lines[0], "a" * 70 + suffix)

    def test_dch_zero_one_two_and_ten_are_clipped_at_the_right_edge(self):
        with Shitty(columns=80, rows=30) as terminal:
            terminal.write(b"a" * 70 + b"1234567890" + b"a" * 70 + b"1234567890")
            expected = (
                (b"\x1b[P", "234567890" + " "),
                (b"\x1b[1P", "34567890" + "  "),
                (b"\x1b[2P", "567890" + " " * 4),
                (b"\x1b[10P", " " * 10),
            )
            for operation, suffix in expected:
                terminal.write(b"\x1b[1;71H" + operation)
                self.assertEqual(terminal.snapshot().lines[0], "a" * 70 + suffix)

    def test_el_zero_one_and_two_erase_the_exact_ranges(self):
        with Shitty(columns=80, rows=30) as terminal:
            terminal.write(b"a" * 240)
            terminal.write(b"\x1b[1;71H\x1b[K")
            terminal.write(b"\x1b[2;71H\x1b[1K")
            terminal.write(b"\x1b[3;71H\x1b[2K")
            self.assertEqual(
                terminal.snapshot().lines[:3],
                [
                    "a" * 70 + " " * 10,
                    " " * 71 + "a" * 9,
                    " " * 80,
                ],
            )

    @unittest.expectedFailure
    def test_el_updates_soft_wrap_only_when_the_line_boundary_is_erased(self):
        operations = (
            (b"\x1b[3;41H\x1b[K", True),
            (b"\x1b[3;1H\x1b[K", False),
            (b"\x1b[3;41H\x1b[1K", True),
            (b"\x1b[3;41H\x1b[2K", False),
        )
        for operation, wrapped in operations:
            with self.subTest(operation=operation):
                with Shitty(columns=80, rows=30) as terminal:
                    terminal.write(b"a" * 80 + b"a" * 89)
                    # xterm.js stores the link on the continuation row;
                    # Shitty stores the equivalent link on its predecessor.
                    self.assertTrue(has_soft_wrap(terminal.model_snapshot(), 1))
                    terminal.write(operation)
                    self.assertEqual(has_soft_wrap(terminal.model_snapshot(), 1), wrapped)

    @unittest.expectedFailure
    def test_ed2_can_push_the_visible_page_into_scrollback(self):
        # xterm.js enables this with scrollOnEraseInDisplay. Shitty has no
        # corresponding policy option and implements the regular ECMA erase.
        with Shitty(columns=8, rows=4, save_lines=20) as terminal:
            terminal.write(b"a" * 16)
            before = terminal.scrollback_state()[0]
            terminal.write(b"\x1b[2J")
            self.assertEqual(terminal.scrollback_state()[0], before + 2)

    def test_ed_zero_one_two_and_wrapped_lines_match_xtermjs(self):
        with Shitty(columns=8, rows=7) as terminal:
            terminal.write(b"a" * 56 + b"\x1b[6;5H\x1b[J")
            self.assertEqual(
                terminal.snapshot().lines,
                ["aaaaaaaa"] * 5 + ["aaaa    ", "        "],
            )

        with Shitty(columns=8, rows=7) as terminal:
            terminal.write(b"a" * 56 + b"\x1b[6;5H\x1b[1J")
            self.assertEqual(
                terminal.snapshot().lines,
                ["        "] * 5 + ["     aaa", "aaaaaaaa"],
            )

        with Shitty(columns=8, rows=7) as terminal:
            terminal.write(b"a" * 56 + b"\x1b[6;5H\x1b[2J")
            self.assertEqual(terminal.snapshot().lines, ["        "] * 7)

        with Shitty(columns=8, rows=7) as terminal:
            terminal.write(b"a" * 8 + b"a" * 17)
            self.assertTrue(has_soft_wrap(terminal.model_snapshot(), 1))
            terminal.write(b"\x1b[3;5H\x1b[1J")
            self.assertFalse(has_soft_wrap(terminal.model_snapshot(), 1))

    def test_zero_width_space_does_not_advance_or_grow_the_page(self):
        with Shitty(columns=8, rows=3) as terminal:
            before = terminal.scrollback_state()
            terminal.write("\u200b".encode())
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 0))
            self.assertEqual(snapshot.lines, ["        "] * 3)
            self.assertEqual(terminal.scrollback_state(), before)

    def test_combining_character_joins_the_base_in_one_parse(self):
        with Shitty(columns=8, rows=3) as terminal:
            terminal.write("e\u0301".encode())
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.cell(0, 0).grapheme, (ord("e"), 0x301))
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 0))


if __name__ == "__main__":
    unittest.main()
