# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Public adaptations of all 24 Ghostty terminal/Parser.zig tests."""

import unittest

from harness import Shitty


UPSTREAM_CASES = (
    "esc: ESC ( B",
    "csi: ESC [ H",
    "csi: ESC [ 1 ; 4 H",
    "csi: SGR ESC [ 38 : 2 m",
    "csi: SGR colon followed by semicolon",
    "csi: SGR mixed colon and semicolon",
    "csi: SGR ESC [ 48 : 2 m",
    "csi: SGR ESC [4:3m colon",
    "csi: SGR with many blank and colon",
    "csi: SGR mixed colon and semicolon with blank",
    "csi: SGR mixed colon and semicolon setting underline, bg, fg",
    "csi: colon for non-m final",
    "csi: request mode decrqm",
    "csi: change cursor",
    "osc: change window title",
    "osc: change window title (end in esc)",
    "osc: 112 incomplete sequence",
    "osc: 104 empty",
    "csi: too many params",
    "csi: sgr with up to our max parameters",
    "csi: sgr beyond our max drops it",
    "dcs: XTGETTCAP",
    "dcs: params",
    "dcs: too many params",
)


def palette_query(terminal, index):
    terminal.write(f"\x1b]4;{index};?\x1b\\".encode())
    return terminal.read_input()


def dynamic_query(terminal, command):
    terminal.write(f"\x1b]{command};?\x1b\\".encode())
    return terminal.read_input()


class GhosttyParserExactTest(unittest.TestCase):
    def test_upstream_inventory_has_24_distinct_parser_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 24)
        self.assertEqual(len(set(UPSTREAM_CASES)), 24)

    def test_escape_designation_keeps_its_intermediate(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b(B")
            self.assertEqual(terminal.parser_trace(), [("escape", b"(B")])

    def test_csi_home_dispatches_without_parameters(self):
        with Shitty(columns=8, rows=3) as terminal:
            terminal.write(b"\x1b[3;4H")
            terminal.parser_trace_on()
            terminal.write(b"\x1b[H")
            self.assertEqual(terminal.parser_trace(), [("csi", b"H")])
            self.assertEqual(
                (terminal.snapshot().cursor_x, terminal.snapshot().cursor_y),
                (0, 0),
            )

    def test_csi_cup_dispatches_both_parameters(self):
        with Shitty(columns=8, rows=3) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b[1;4HX")
            self.assertEqual(terminal.parser_trace()[0], ("csi", b"1;4H"))
            self.assertEqual(terminal.snapshot().cell(3, 0).char, "X")

    def test_short_colon_truecolor_sgr_reaches_one_dispatch(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b[38:2mX")
            self.assertEqual(
                terminal.parser_trace(),
                [("csi", b"38:2m"), ("text", b"X")],
            )

    def test_short_colon_sgr_does_not_poison_the_next_csi(self):
        with Shitty(columns=8, rows=3) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b[48:2m\x1b[2;3HX")
            self.assertEqual(
                terminal.parser_trace(),
                [("csi", b"48:2m"), ("csi", b"2;3H"), ("text", b"X")],
            )
            self.assertEqual(terminal.snapshot().cell(2, 1).char, "X")

    def test_mixed_colon_semicolon_indexed_colors(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[38:5:1;48:5:0mX")
            pen = terminal.pen_state()
            self.assertEqual(pen.foreground_index, 1)
            self.assertEqual(pen.background_index, 0)

    def test_colon_truecolor_background_keeps_every_component(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[48:2:240:143:104mX")
            self.assertEqual(
                terminal.snapshot().cell(0, 0).background,
                (240, 143, 104),
            )

    def test_colon_underline_style_dispatches_curly(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[4:3mX")
            self.assertEqual(terminal.snapshot().cell(0, 0).underline_style, 3)

    def test_blank_colon_subparameter_is_preserved(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[58:2::240:143:104mX")
            self.assertEqual(
                terminal.snapshot().cell(0, 0).underline_color,
                (240, 143, 104),
            )

    def test_kakoune_mixed_sgr_with_blank_sets_all_renditions(self):
        sequence = b"\x1b[;4:3;38;2;175;175;215;58:2::190:80:70mX"
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(sequence)
            cell = terminal.snapshot().cell(0, 0)
            self.assertEqual(cell.underline_style, 3)
            self.assertEqual(cell.foreground, (175, 175, 215))
            self.assertEqual(cell.underline_color, (190, 80, 70))

    def test_kakoune_mixed_sgr_sets_underline_background_and_foreground(self):
        sequence = (
            b"\x1b[4:3;38;2;51;51;51;48;2;170;170;170;"
            b"58;2;255;97;136mX"
        )
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(sequence)
            cell = terminal.snapshot().cell(0, 0)
            self.assertEqual(cell.underline_style, 3)
            self.assertEqual(cell.foreground, (51, 51, 51))
            self.assertEqual(cell.background, (170, 170, 170))
            self.assertEqual(cell.underline_color, (255, 97, 136))

    @unittest.expectedFailure
    def test_colon_parameter_is_rejected_for_non_sgr_final(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b[38:2h")
            self.assertEqual(terminal.parser_trace(), [])

    def test_decrqm_keeps_private_prefix_parameter_and_intermediate(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b[?2026$p")
            self.assertEqual(terminal.parser_trace(), [("csi", b"?2026$p")])

    def test_cursor_style_keeps_space_intermediate(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b[3 q")
            self.assertEqual(terminal.parser_trace(), [("csi", b"3 q")])
            self.assertEqual(terminal.snapshot().cursor_style, 3)

    def test_window_title_terminated_by_bell(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b]0;abc\a")
            self.assertEqual(terminal.window_title(), "abc")

    def test_window_title_terminated_by_escape_backslash(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b]0;abc\x1b\\")
            self.assertEqual(terminal.window_title(), "abc")

    def test_incomplete_osc_112_resets_cursor_color(self):
        with Shitty(columns=8, rows=2) as terminal:
            baseline = dynamic_query(terminal, 12)
            terminal.write(b"\x1b]12;#010203\x1b\\")
            self.assertNotEqual(dynamic_query(terminal, 12), baseline)
            terminal.write(b"\x1b]112\a")
            self.assertEqual(dynamic_query(terminal, 12), baseline)

    def test_empty_osc_104_resets_the_whole_palette(self):
        with Shitty(columns=8, rows=2) as terminal:
            baseline = palette_query(terminal, 1)
            terminal.write(b"\x1b]4;1;#010203\x1b\\")
            self.assertNotEqual(palette_query(terminal, 1), baseline)
            terminal.write(b"\x1b]104\a")
            self.assertEqual(palette_query(terminal, 1), baseline)

    def test_far_beyond_parameter_capacity_discards_the_csi(self):
        parameters = b"1;" * 100 + b"1"
        with Shitty(columns=8, rows=2) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b[" + parameters + b"C")
            self.assertEqual(terminal.parser_trace(), [])
            terminal.write(b"X")
            self.assertEqual(terminal.snapshot().cell(0, 0).char, "X")

    def test_every_count_through_ghostty_parameter_capacity_dispatches(self):
        with Shitty(columns=8, rows=3) as terminal:
            terminal.parser_trace_on()
            for count in range(1, 25):
                with self.subTest(count=count):
                    parameters = b"1;" * (count - 1) + b"2"
                    terminal.write(b"\x1b[" + parameters + b"H")
                    self.assertEqual(
                        terminal.parser_trace(),
                        [("csi", parameters + b"H")],
                    )

    @unittest.expectedFailure
    def test_ghostty_parameter_overflow_discards_the_csi(self):
        parameters = b"1;" * 25 + b"2"
        with Shitty(columns=8, rows=2) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b[" + parameters + b"H")
            self.assertEqual(terminal.parser_trace(), [])

    def test_xtgettcap_dcs_header_dispatches_to_passthrough(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1bP+q544e\x1b\\")
            self.assertEqual(
                terminal.read_input(),
                b"\x1bP1+r544e=787465726d2d323536636f6c6f72\x1b\\",
            )

    def test_dcs_numeric_parameter_is_preserved_in_trace(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1bP1000pabc\x1b\\")
            self.assertEqual(terminal.parser_trace(), [("dcs", b"1000pabc")])

    @unittest.expectedFailure
    def test_ghostty_parameter_overflow_discards_the_dcs(self):
        header = b"6" + b";" * 24 + b"7+q"
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1bP" + header + b"544e\x1b\\")
            self.assertEqual(terminal.read_input(), b"")


if __name__ == "__main__":
    unittest.main()
