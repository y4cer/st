# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty, TEST_PLATFORM


RELEASE = 0
PRESS = 1
KEY_EQUAL = 61
KEY_MINUS = 45
MOD_SHIFT = 1
MOD_CONTROL = 2
MOD_SUPER = 8

# The default bindings differ per platform: Cmd chords on macOS (which
# deliver no text event), Ctrl chords with their typed text on Linux.
if TEST_PLATFORM == "cocoa":
    FONT_INC = (KEY_EQUAL, None, MOD_SUPER)
    FONT_DEC = (KEY_MINUS, None, MOD_SUPER)
else:
    FONT_INC = (KEY_EQUAL, "+", MOD_CONTROL | MOD_SHIFT)
    FONT_DEC = (KEY_MINUS, "-", MOD_CONTROL)


class OutputScaleTest(unittest.TestCase):
    @staticmethod
    def shortcut(terminal, key, text, modifiers):
        terminal.frontend_key_event(key, PRESS, modifiers=modifiers)
        if text is not None:
            terminal.frontend_text_event(text, modifiers=modifiers)
        terminal.frontend_key_event(key, RELEASE, modifiers=modifiers)

    def assert_geometry(self, terminal, state, columns, rows, scale, border):
        self.assertEqual(state[0], 16)
        self.assertEqual(state[5:7], (columns, rows))
        self.assertEqual(state[7], scale)
        self.assertEqual(state[8], border)
        self.assertEqual(state[3], 2 * border + columns * state[1])
        self.assertEqual(state[4], 2 * border + rows * state[2])
        self.assertEqual(terminal.winsize(), (columns, rows))

    def test_output_scale_rebuilds_fonts_and_preserves_grid(self):
        with Shitty(
            columns=40,
            rows=8,
            glyph_px=8,
            glyph_py=16,
            extra_arguments=("-fontsize", "16", "-border", "2"),
        ) as terminal:
            self.shortcut(terminal, *FONT_INC)
            self.shortcut(terminal, *FONT_DEC)
            terminal.write(b"scale")
            initial = terminal.font_state()
            self.assert_geometry(terminal, initial, 40, 8, 1000, 2)
            before = terminal.snapshot()

            terminal.frontend_content_scale(3, 2)
            scaled_150 = terminal.font_state()
            self.assert_geometry(terminal, scaled_150, 40, 8, 1500, 3)
            self.assertGreater(scaled_150[1], initial[1])
            self.assertGreater(scaled_150[2], initial[2])
            self.assertGreater(terminal.snapshot().refresh_count, before.refresh_count)

            terminal.frontend_content_scale(2, 1)
            scaled_200 = terminal.font_state()
            self.assert_geometry(terminal, scaled_200, 40, 8, 2000, 4)
            self.assertGreater(scaled_200[1], scaled_150[1])
            self.assertGreater(scaled_200[2], scaled_150[2])

            terminal.frontend_content_scale(3, 2)
            returned = terminal.font_state()
            self.assert_geometry(terminal, returned, 40, 8, 1500, 3)
            self.assertEqual(returned[1:5], scaled_150[1:5])


if __name__ == "__main__":
    unittest.main()
