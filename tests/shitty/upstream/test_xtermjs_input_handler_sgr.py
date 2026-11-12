# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Public adaptations of xterm.js InputHandler cases 41 through 60."""

import unittest

from harness import Shitty


UPSTREAM_CASES = (
    "text attributes: underline",
    "text attributes: blink",
    "text attributes: inverse",
    "text attributes: invisible",
    "text attributes: strikethrough",
    "text attributes: colormode palette 16",
    "text attributes: colormode palette 256",
    "text attributes: colormode RGB",
    "text attributes: colormode transition RGB to 256",
    "text attributes: colormode transition RGB to 16",
    "text attributes: colormode transition 16 to 256",
    "text attributes: colormode transition 256 to 16",
    "text attributes: should zero missing RGB values",
    "colon notation: CSI 38:2::50:100:150 m",
    "colon notation: CSI 38:2::50:100: m",
    "colon notation: CSI 38:2::50:: m",
    "colon notation: CSI 38:2:::: m",
    "colon notation: CSI 38;2::50:100:150 m",
    "colon notation: CSI 38;2;50:100:150 m",
    "colon notation: CSI 38;2;50;100:150 m",
)


def sgr_report(terminal):
    terminal.write(b"\x1bP$qm\x1b\\")
    return terminal.read_input()


class XtermJsInputHandlerSgrTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 20)
        self.assertEqual(len(set(UPSTREAM_CASES)), 20)

    def test_sgr_underline_and_24_reset(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[4m")
            self.assertTrue(terminal.pen_state().underline)
            terminal.write(b"\x1b[24m")
            self.assertFalse(terminal.pen_state().underline)

    def test_sgr_blink_and_25_reset(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[5m")
            self.assertTrue(terminal.pen_state().blink)
            terminal.write(b"\x1b[25m")
            self.assertFalse(terminal.pen_state().blink)

    def test_sgr_inverse_and_27_reset(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[7m")
            self.assertTrue(terminal.pen_state().inverse)
            terminal.write(b"\x1b[27m")
            self.assertFalse(terminal.pen_state().inverse)

    def test_sgr_conceal_and_28_reset(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[8mX")
            self.assertTrue(terminal.snapshot().cell(0, 0).conceal)
            terminal.write(b"\x1b[28mY")
            self.assertFalse(terminal.snapshot().cell(1, 0).conceal)

    def test_sgr_strike_and_29_reset(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[9mX")
            self.assertTrue(terminal.snapshot().cell(0, 0).strike)
            terminal.write(b"\x1b[29mY")
            self.assertFalse(terminal.snapshot().cell(1, 0).strike)

    def test_sgr_sixteen_color_palette_and_default_reset(self):
        with Shitty(columns=8, rows=2) as terminal:
            default_report = sgr_report(terminal)
            for index in range(8):
                terminal.write(f"\x1b[{index + 30};{index + 40}m".encode())
                pen = terminal.pen_state()
                self.assertEqual((pen.foreground_index, pen.background_index), (index, index))
            terminal.write(b"\x1b[39;49m")
            self.assertEqual(sgr_report(terminal), default_report)

    def test_sgr_every_256_color_palette_index_and_default_reset(self):
        with Shitty(columns=8, rows=2) as terminal:
            default_report = sgr_report(terminal)
            for index in range(256):
                terminal.write(f"\x1b[38;5;{index};48;5;{index}m".encode())
                pen = terminal.pen_state()
                self.assertEqual((pen.foreground_index, pen.background_index), (index, index))
            terminal.write(b"\x1b[39;49m")
            self.assertEqual(sgr_report(terminal), default_report)

    def test_sgr_rgb_foreground_background_and_default_reset(self):
        with Shitty(columns=8, rows=2) as terminal:
            default_report = sgr_report(terminal)
            terminal.write(b"\x1b[38;2;1;2;3;48;2;4;5;6m")
            pen = terminal.pen_state()
            self.assertEqual(pen.foreground, (1, 2, 3))
            self.assertEqual(pen.background, (4, 5, 6))
            terminal.write(b"\x1b[39;49m")
            self.assertEqual(sgr_report(terminal), default_report)

    def test_sgr_transition_rgb_to_256(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[38;2;1;2;3;48;2;4;5;6m\x1b[38;5;255;48;5;255m")
            pen = terminal.pen_state()
            self.assertEqual((pen.foreground_index, pen.background_index), (255, 255))

    def test_sgr_transition_rgb_to_sixteen_color(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[38;2;1;2;3;48;2;4;5;6m\x1b[37;47m")
            pen = terminal.pen_state()
            self.assertEqual((pen.foreground_index, pen.background_index), (7, 7))

    def test_sgr_transition_sixteen_to_256_color(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[37;47m\x1b[38;5;255;48;5;255m")
            pen = terminal.pen_state()
            self.assertEqual((pen.foreground_index, pen.background_index), (255, 255))

    def test_sgr_transition_256_to_sixteen_color(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[38;5;255;48;5;255m\x1b[37;47m")
            pen = terminal.pen_state()
            self.assertEqual((pen.foreground_index, pen.background_index), (7, 7))

    @unittest.expectedFailure
    def test_semicolon_rgb_zeros_missing_green_and_blue(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[38;2;1;2;3m\x1b[38;2;5m")
            self.assertEqual(terminal.pen_state().foreground, (5, 0, 0))

    def test_colon_rgb_matches_semicolon_with_all_components(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[38:2::50:100:150m")
            self.assertEqual(terminal.pen_state().foreground, (50, 100, 150))

    def test_colon_rgb_zeros_a_missing_blue_component(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[38:2::50:100:m")
            self.assertEqual(terminal.pen_state().foreground, (50, 100, 0))

    def test_colon_rgb_zeros_missing_green_and_blue_components(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[38:2::50::m")
            self.assertEqual(terminal.pen_state().foreground, (50, 0, 0))

    def test_colon_rgb_zeros_all_missing_components(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[38:2::::m")
            self.assertEqual(terminal.pen_state().foreground, (0, 0, 0))

    @unittest.expectedFailure
    def test_mixed_semicolon_then_colon_rgb_matches_plain_semicolons(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[38;2::50:100:150m")
            self.assertEqual(terminal.pen_state().foreground, (50, 100, 150))

    def test_mixed_semicolon_rgb_then_colon_components(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[38;2;50:100:150m")
            self.assertEqual(terminal.pen_state().foreground, (50, 100, 150))

    def test_mixed_semicolon_rgb_with_colon_tail_component(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[38;2;50;100:150m")
            self.assertEqual(terminal.pen_state().foreground, (50, 100, 150))


if __name__ == "__main__":
    unittest.main()
