# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Public adaptations of xterm.js InputHandler cases 21 through 40."""

import unittest

from harness import Shitty


UPSTREAM_CASES = (
    "print: should join combining characters split across parse calls",
    "print: should repeat preceding grapheme cluster via REP",
    "print: should not repeat when REP has no preceding join state",
    "print: should not repeat after an intervening escape sequence",
    "print: should clear cells to the right on early wrap-around",
    "print: should strip soft hyphens (U+00AD)",
    "ISO-2022: should map G0 line drawing via ESC ( 0",
    "ISO-2022: should map G1 line drawing after ESC ) 0 and SO",
    "ISO-2022: should restore charset and glevel on ESC 7 / ESC 8",
    "alt screen: should handle DECSET/DECRST 47",
    "alt screen: should handle DECSET/DECRST 1047",
    "alt screen: should handle DECSET/DECRST 1048",
    "alt screen: should handle DECSET/DECRST 1049",
    "alt screen: DECSET/DECRST 1049 maintains saved cursor for alt buffer",
    "alt screen: DECSET 1049 clears alt buffer with erase attributes",
    "text attributes: bold",
    "text attributes: dim",
    "text attributes: SGR 221 resets bold only (kitty)",
    "text attributes: SGR 222 resets faint only (kitty)",
    "text attributes: italic",
)


class XtermJsInputHandlerTextTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 20)
        self.assertEqual(len(set(UPSTREAM_CASES)), 20)

    def test_combining_character_joins_across_parse_calls(self):
        with Shitty(columns=8, rows=3) as terminal:
            terminal.write_chunks(b"e", "\u0301".encode())
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.cell(0, 0).grapheme, (ord("e"), 0x301))
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 0))

    @unittest.expectedFailure
    def test_rep_repeats_the_preceding_grapheme_cluster(self):
        with Shitty(columns=8, rows=3) as terminal:
            terminal.write("e\u0301\x1b[2b".encode())
            snapshot = terminal.model_snapshot()
            self.assertEqual(
                tuple(snapshot.cell(column, 0).grapheme for column in range(3)),
                ((ord("e"), 0x301),) * 3,
            )
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (3, 0))

    def test_rep_without_a_preceding_graphic_character_is_a_noop(self):
        with Shitty(columns=8, rows=3) as terminal:
            terminal.write(b"\x1b[2b")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0], " " * 8)
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 0))

    @unittest.expectedFailure
    def test_rep_does_not_cross_an_intervening_escape_sequence(self):
        with Shitty(columns=8, rows=3) as terminal:
            terminal.write(b"a\x1b[0m\x1b[2b")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0], "a" + " " * 7)
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 0))

    @unittest.expectedFailure
    def test_early_wide_wrap_clears_the_stale_rightmost_cell(self):
        with Shitty(columns=5, rows=5, save_lines=1) as terminal:
            terminal.write(b"12345\x1b[1;1H" + "￥￥￥".encode())
            snapshot = terminal.snapshot()
            self.assertEqual(
                tuple(snapshot.cell(column, 0).char for column in range(5)),
                ("￥", " ", "￥", " ", " "),
            )
            self.assertEqual(snapshot.cell(0, 1).char, "￥")

    @unittest.expectedFailure
    def test_soft_hyphens_are_stripped_without_advancing(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write("Soft\u00adhy\u00adphen".encode())
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0][:10], "Softhyphen")
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (10, 0))

    def test_g0_dec_line_drawing_maps_only_while_designated(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b(0q\x1b(Bq")
            self.assertEqual(terminal.snapshot().lines[0][:2], "─q")

    def test_g1_dec_line_drawing_maps_between_so_and_si(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b)0\x0eq\x0f\x1b(Bq")
            self.assertEqual(terminal.snapshot().lines[0][:2], "─q")

    def test_decsc_decrc_restore_charset_designation_and_gl_level(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b)0\x0e\x1b7\x0f\x1b(B\x1b8q")
            self.assertEqual(terminal.snapshot().cell(0, 0).char, "─")

    def test_mode_47_switches_buffers_without_restoring_cursor_or_rendition(self):
        with Shitty(columns=80, rows=30) as terminal:
            terminal.write(b"\x1b[?47h\r\n\x1b[31mJUNK\x1b[?47lTEST")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[0], " " * 80)
            self.assertEqual(snapshot.lines[1][4:8], "TEST")
            self.assertEqual(snapshot.cell(4, 1).foreground_index, 1)

    def test_mode_1047_switches_buffers_without_restoring_cursor_or_rendition(self):
        with Shitty(columns=80, rows=30) as terminal:
            terminal.write(b"\x1b[?1047h\r\n\x1b[31mJUNK\x1b[?1047lTEST")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[0], " " * 80)
            self.assertEqual(snapshot.lines[1][4:8], "TEST")
            self.assertEqual(snapshot.cell(4, 1).foreground_index, 1)

    def test_mode_1048_restores_cursor_and_rendition_without_switching(self):
        with Shitty(columns=80, rows=30) as terminal:
            terminal.write(b"\x1b[?1048h\r\n\x1b[31mJUNK\x1b[?1048lTEST")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[0][:4], "TEST")
            self.assertEqual(snapshot.lines[1][:4], "JUNK")
            self.assertNotEqual(snapshot.cell(0, 0).foreground_index, 1)
            self.assertEqual(snapshot.cell(0, 1).foreground_index, 1)

    def test_mode_1049_switches_buffer_and_restores_cursor_and_rendition(self):
        with Shitty(columns=80, rows=30) as terminal:
            terminal.write(b"\x1b[?1049h\r\n\x1b[31mJUNK\x1b[?1049lTEST")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[0][:4], "TEST")
            self.assertEqual(snapshot.lines[1], " " * 80)
            self.assertNotEqual(snapshot.cell(0, 0).foreground_index, 1)

    def test_mode_1049_keeps_an_independent_saved_cursor_in_alternate_buffer(self):
        with Shitty(columns=80, rows=30) as terminal:
            terminal.write(b"\x1b[?1049h\r\n\x1b[31m\x1b[s\x1b[?1049lTEST")
            primary = terminal.model_snapshot()
            self.assertEqual(primary.lines[0][:4], "TEST")
            self.assertNotEqual(primary.cell(0, 0).foreground_index, 1)

            terminal.write(b"\x1b[?1049h\x1b[uTEST")
            alternate = terminal.model_snapshot()
            self.assertEqual(alternate.lines[1][:4], "TEST")
            self.assertEqual(alternate.cell(0, 1).foreground_index, 1)

    @unittest.expectedFailure
    def test_mode_1049_clears_alternate_with_current_erase_attributes(self):
        with Shitty(columns=80, rows=30) as terminal:
            terminal.write(b"\x1b[42m\x1b[?1049h")
            cell = terminal.model_snapshot().cell(10, 20)
            self.assertEqual(cell.char, " ")
            self.assertEqual(cell.background_index, 2)

    def test_sgr_bold_and_22_reset(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[1m")
            self.assertTrue(terminal.pen_state().bold)
            terminal.write(b"\x1b[22m")
            self.assertFalse(terminal.pen_state().bold)

    def test_sgr_faint_and_22_reset(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[2m")
            self.assertTrue(terminal.pen_state().faint)
            terminal.write(b"\x1b[22m")
            self.assertFalse(terminal.pen_state().faint)

    @unittest.expectedFailure
    def test_kitty_sgr_221_resets_bold_without_resetting_faint(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[1;2m\x1b[221m")
            pen = terminal.pen_state()
            self.assertFalse(pen.bold)
            self.assertTrue(pen.faint)

    @unittest.expectedFailure
    def test_kitty_sgr_222_resets_faint_without_resetting_bold(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[1;2m\x1b[222m")
            pen = terminal.pen_state()
            self.assertTrue(pen.bold)
            self.assertFalse(pen.faint)

    def test_sgr_italic_and_23_reset(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[3m")
            self.assertTrue(terminal.pen_state().italic)
            terminal.write(b"\x1b[23m")
            self.assertFalse(terminal.pen_state().italic)


if __name__ == "__main__":
    unittest.main()
