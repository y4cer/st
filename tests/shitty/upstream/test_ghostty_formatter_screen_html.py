# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


UPSTREAM_CASES = (
    "Screen plain multiline",
    "Screen plain with selection",
    "Screen vt with cursor position",
    "Screen vt with style",
    "Screen vt with hyperlink",
    "Screen vt with protection",
    "Screen vt with kitty keyboard",
    "Screen vt with charsets",
    "Terminal vt with scrolling region",
    "Terminal vt with modes",
    "Terminal vt with tabstops",
    "Terminal vt with keyboard modes",
    "Terminal vt with pwd",
    "Page html with multiple styles",
    "Page html plain text",
    "Page html with colors",
    "TerminalFormatter html with palette",
    "Page html with background and foreground colors",
    "Page html with escaping",
    "Page html with unicode as numeric entities",
)


def select(terminal, start, end):
    terminal.select_start(*start)
    terminal.select_update(*end)
    return terminal.select_finish()


def decrqss(terminal, setting):
    terminal.write(b"\x1bP$q" + setting + b"\x1b\\")
    return terminal.read_input()


def mode_query(terminal, mode, private=True):
    prefix = "?" if private else ""
    terminal.write(f"\x1b[{prefix}{mode}$p".encode())
    return terminal.read_input()


def palette_query(terminal, *indices):
    terminal.write(
        b"\x1b]4;" + b";".join(f"{index};?".encode() for index in indices) + b"\x1b\\"
    )
    return terminal.read_input()


class GhosttyFormatterScreenHtmlTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 20)
        self.assertEqual(len(set(UPSTREAM_CASES)), 20)

    def test_active_screen_plain_copy_keeps_hard_line_boundaries(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"hello\r\nworld")

            self.assertEqual(select(terminal, (0, 0), (5, 1)), b"hello\nworld")

    def test_active_screen_plain_copy_can_select_one_middle_row(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"line1\r\nline2\r\nline3")

            self.assertEqual(select(terminal, (0, 1), (5, 1)), b"line2")

    def test_cursor_position_is_observable_through_cpr(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"hello\r\nworld\x1b[6n")

            self.assertEqual(terminal.read_input(), b"\x1b[2;6R")
            self.assertEqual(terminal.snapshot().cursor_x, 5)
            self.assertEqual(terminal.snapshot().cursor_y, 1)

    def test_current_style_is_observable_and_replayable_through_decrqss(self):
        with Shitty(columns=80, rows=24, save_lines=0) as source:
            source.write(b"\x1b[1;31mhello")
            report = decrqss(source, b"m")
            source_pen = source.pen_state()

        with Shitty(columns=80, rows=24, save_lines=0) as replay:
            replay.write(b"\x1b[" + report[5:-2] + b"X")
            replay_pen = replay.pen_state()

            self.assertEqual(replay_pen, source_pen)
            self.assertTrue(replay.snapshot().cell(0, 0).bold)
            self.assertEqual(replay.snapshot().cell(0, 0).foreground, (170, 0, 0))

    def test_active_hyperlink_applies_to_later_text_until_closed(self):
        uri = b"http://example.com"
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"\x1b]8;;" + uri + b"\x1b\\helloX")

            self.assertEqual(terminal.hyperlink(0, 0), uri.decode())
            self.assertEqual(terminal.hyperlink(5, 0), uri.decode())

    def test_active_dec_protection_is_reported_and_applies_to_later_text(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b'\x1b[1"qhelloX')
            snapshot = terminal.snapshot()

            self.assertEqual(decrqss(terminal, b'"q'), b'\x1bP1$r1"q\x1b\\')
            self.assertTrue(all(snapshot.cell(column, 0).protected for column in range(6)))

    def test_kitty_keyboard_flags_are_observable_through_the_protocol_query(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"\x1b[=3;1uhello\x1b[?u")

            self.assertEqual(terminal.read_input(), b"\x1b[?3u")

    def test_g0_designation_survives_while_g1_is_invoked(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"\x1b(0\x0ehello\x0fq")
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.lines[0][:5], "hello")
            self.assertEqual(snapshot.cell(5, 0).char, "\u2500")

    def test_scrolling_region_is_observable_through_decrqss(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"\x1b[6;21rhello")

            self.assertEqual(decrqss(terminal, b"r"), b"\x1bP1$r6;21r\x1b\\")

    def test_nondefault_terminal_modes_report_their_live_state(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"\x1b[?2004h\x1b[?1000h\x1b[?7lhello")

            self.assertEqual(mode_query(terminal, 2004), b"\x1b[?2004;1$y")
            self.assertEqual(mode_query(terminal, 1000), b"\x1b[?1000;1$y")
            self.assertEqual(mode_query(terminal, 7), b"\x1b[?7;2$y")

    def test_custom_tabstops_replace_the_default_set(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(
                b"\x1b[3g\x1b[5G\x1bH\x1b[15G\x1bH\x1b[30G\x1bHhello"
            )

            self.assertTrue(terminal.tab_stop(4))
            self.assertTrue(terminal.tab_stop(14))
            self.assertTrue(terminal.tab_stop(29))
            self.assertFalse(terminal.tab_stop(8))

    def test_modify_other_keys_level_two_is_observable_in_encoded_input(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"\x1b[>4;2mhello")
            terminal.char("a", modifiers=1)

            self.assertEqual(terminal.read_input(), b"\x1b[27;2;97~")

    def test_osc7_publishes_the_current_working_directory(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"\x1b]7;file://host/home/user\x1b\\hello")

            self.assertEqual(terminal.current_cwd(), b"/home/user")

    def test_html_style_source_runs_remain_distinct_in_the_public_model(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"\x1b[1mbold\x1b[3mitalic\x1b[0mnormal")
            snapshot = terminal.snapshot()

            for column in range(4):
                self.assertTrue(snapshot.cell(column, 0).bold)
                self.assertFalse(snapshot.cell(column, 0).italic)
            for column in range(4, 10):
                self.assertTrue(snapshot.cell(column, 0).bold)
                self.assertTrue(snapshot.cell(column, 0).italic)
            for column in range(10, 16):
                self.assertFalse(snapshot.cell(column, 0).bold)
                self.assertFalse(snapshot.cell(column, 0).italic)

    def test_html_plain_source_is_available_through_plain_copy(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"hello, world")

            self.assertEqual(select(terminal, (0, 0), (12, 0)), b"hello, world")

    def test_html_palette_color_source_remains_indexed_in_the_public_model(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"\x1b[31;44mcolored")
            snapshot = terminal.model_snapshot()

            for column in range(7):
                self.assertEqual(snapshot.cell(column, 0).foreground_index, 1)
                self.assertEqual(snapshot.cell(column, 0).background_index, 4)

    def test_html_palette_source_is_observable_through_osc4_queries(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(
                b"\x1b]4;0;rgb:12/34/56\x1b\\"
                b"\x1b]4;1;rgb:ab/cd/ef\x1b\\"
                b"\x1b]4;255;rgb:ff/00/ff\x1b\\test"
            )
            response = palette_query(terminal, 0, 1, 255)

            self.assertIn(b"\x1b]4;0;rgb:1212/3434/5656\x1b\\", response)
            self.assertIn(b"\x1b]4;1;rgb:abab/cdcd/efef\x1b\\", response)
            self.assertIn(b"\x1b]4;255;rgb:ffff/0000/ffff\x1b\\", response)

    def test_html_wrapper_color_source_recolors_default_cells(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(
                b"\x1b]10;rgb:ab/cd/ef\x1b\\"
                b"\x1b]11;rgb:12/34/56\x1b\\hello"
            )
            snapshot = terminal.snapshot()

            for column in range(5):
                self.assertEqual(snapshot.cell(column, 0).foreground, (0xAB, 0xCD, 0xEF))
                self.assertEqual(snapshot.cell(column, 0).background, (0x12, 0x34, 0x56))

    def test_html_metacharacter_source_remains_literal_in_plain_copy(self):
        text = b"<tag>&\"'text"
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(text)

            self.assertEqual(select(terminal, (0, 0), (len(text), 0)), text)

    def test_html_numeric_entity_source_keeps_its_unicode_codepoints(self):
        text = "\u2570\u2500 \u276f"
        encoded = text.encode()
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(encoded)
            snapshot = terminal.snapshot()

            self.assertEqual(select(terminal, (0, 0), (4, 0)), encoded)
            self.assertEqual(tuple(snapshot.cell(column, 0).char for column in range(4)), tuple(text))


if __name__ == "__main__":
    unittest.main()
